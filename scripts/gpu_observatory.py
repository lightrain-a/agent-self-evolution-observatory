#!/usr/bin/env python3
"""Read-only, low-overhead GPU telemetry collector and authenticated relay.

No GPU kernels, NVML mutation, process termination or remote execution.
Only public aggregate GPU metrics are served by the HTTP API.
"""
from __future__ import annotations

import argparse
import csv
from collections import deque
import hashlib
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
from pathlib import Path
import subprocess
import threading
import time
from urllib import request, error

HOSTS = ("69", "42", "52")
ORIGIN = "https://agent-evolution.lightrain.asia"
GPU_QUERY = "index,name,utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw,power.limit"
MAX_BODY = 32768
STALE_AFTER = 35
HISTORY_SIZE = 360


def number(raw, default=None):
    try:
        value = float(str(raw).strip().replace("MiB", "").replace("W", ""))
        return value if value == value and abs(value) != float("inf") else default
    except (TypeError, ValueError):
        return default


def probe():
    command = ["nvidia-smi", "--query-gpu=" + GPU_QUERY,
               "--format=csv,noheader,nounits"]
    result = subprocess.run(command, capture_output=True, text=True,
                            timeout=8, check=False)
    if result.returncode:
        raise RuntimeError("nvidia-smi failed (exit " + str(result.returncode) + ")")
    records = []
    for fields in csv.reader(io.StringIO(result.stdout)):
        if len(fields) != 8:
            continue
        index = number(fields[0])
        used = number(fields[3])
        total = number(fields[4])
        if index is None or used is None or total is None or total <= 0:
            continue
        records.append({
            "index": int(index),
            "model": fields[1].strip()[:80],
            "util": number(fields[2]),
            "used_mib": used,
            "total_mib": total,
            "temp_c": number(fields[5]),
            "power_w": number(fields[6]),
            "power_limit_w": number(fields[7]),
        })
    if not records:
        raise RuntimeError("nvidia-smi did not return valid GPU metrics")
    return sorted(records, key=lambda item: item["index"])


def safe_gpu(item):
    if not isinstance(item, dict):
        raise ValueError("GPU row is not an object")
    index = item.get("index")
    if not isinstance(index, int) or not 0 <= index <= 128:
        raise ValueError("invalid GPU index")
    model = item.get("model", "")
    if not isinstance(model, str) or not model or len(model) > 80:
        raise ValueError("invalid GPU model")
    out = {"index": index, "model": model}
    for key, limit in (("util", 100), ("used_mib", 300000),
                       ("total_mib", 300000), ("temp_c", 150),
                       ("power_w", 2000), ("power_limit_w", 2000)):
        value = item.get(key)
        if value is None:
            out[key] = None
        elif isinstance(value, (int, float)) and not isinstance(value, bool) and 0 <= value <= limit:
            out[key] = round(float(value), 2)
        else:
            raise ValueError("invalid GPU field: " + key)
    if not out["total_mib"] or out["used_mib"] is None or out["used_mib"] > out["total_mib"] + 2048:
        raise ValueError("invalid GPU memory")
    return out


class Storage:
    def __init__(self):
        self.lock = threading.Lock()
        self.latest = {}
        self.history = {host: deque(maxlen=HISTORY_SIZE) for host in HOSTS}

    def accept(self, host, sample):
        gpus = sample["gpus"]
        now = time.time()
        cleaned = [safe_gpu(gpu) for gpu in gpus]
        if not 0 < len(cleaned) <= 128:
            raise ValueError("bad GPU count")
        if len({g["index"] for g in cleaned}) != len(cleaned):
            raise ValueError("duplicate GPU index")
        sampled_at = number(sample.get("sampled_at"))
        if sampled_at is None or abs(now - sampled_at) > 60:
            raise ValueError("stale or invalid sample timestamp")
        summary = {
            "t": round(sampled_at, 2),
            "avg_util": round(sum((g["util"] or 0) for g in cleaned) / len(cleaned), 1),
            "mem_used_gib": round(sum(g["used_mib"] for g in cleaned) / 1024, 2),
            "mem_total_gib": round(sum(g["total_mib"] for g in cleaned) / 1024, 2),
        }
        with self.lock:
            previous = self.latest.get(host)
            if previous and sampled_at < previous["sampled_at"]:
                return
            self.latest[host] = {"sampled_at": sampled_at, "gpus": cleaned}
            self.history[host].append(summary)

    def snapshot(self):
        now = time.time()
        with self.lock:
            hosts = []
            for host in HOSTS:
                item = self.latest.get(host)
                age = round(now - item["sampled_at"], 1) if item else None
                hosts.append({
                    "id": host,
                    "online": item is not None and age <= STALE_AFTER,
                    "sampled_at": item["sampled_at"] if item else None,
                    "age_s": age,
                    "gpus": item["gpus"] if item else [],
                })
            return {"schema_version": 1, "server_time": now,
                    "stale_after_s": STALE_AFTER, "hosts": hosts}

    def trends(self):
        with self.lock:
            return {"schema_version": 1, "hosts": {
                host: list(self.history[host]) for host in HOSTS}}


def make_handler(tokens, storage):
    class Handler(BaseHTTPRequestHandler):
        server_version = "GpuObservatory/1.0"

        def log_message(self, fmt, *args):
            # Avoid logging bearer materials or sensitive payloads.
            if "/healthz" not in self.path:
                super().log_message(fmt, *args)

        def reply(self, status, value):
            encoded = json.dumps(value, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store, max-age=0")
            self.send_header("Access-Control-Allow-Origin", ORIGIN)
            self.send_header("Vary", "Origin")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def do_GET(self):
            if self.path == "/api/v1/gpus":
                self.reply(200, storage.snapshot())
            elif self.path == "/api/v1/history":
                self.reply(200, storage.trends())
            elif self.path == "/healthz":
                self.reply(200, {"ok": True})
            else:
                self.reply(404, {"error": "not found"})

        def do_POST(self):
            if not self.path.startswith("/api/v1/ingest/"):
                return self.reply(404, {"error": "not found"})
            host = self.path.removeprefix("/api/v1/ingest/")
            if host not in HOSTS:
                return self.reply(404, {"error": "not found"})
            try:
                size = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                return self.reply(400, {"error": "bad content length"})
            if not 0 < size <= MAX_BODY:
                return self.reply(413, {"error": "invalid body size"})
            body = self.rfile.read(size)
            timestamp = self.headers.get("X-Monitor-Timestamp", "")
            signature = self.headers.get("X-Monitor-Signature", "")
            if not timestamp.isdecimal() or abs(time.time() - int(timestamp)) > 60:
                return self.reply(403, {"error": "authentication failed"})
            expected = hmac.new(
                tokens[host].encode(), timestamp.encode() + b"." + body,
                hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(signature, expected):
                return self.reply(403, {"error": "authentication failed"})
            try:
                sample = json.loads(body)
                if not isinstance(sample, dict) or sample.get("host") != host:
                    raise ValueError("host mismatch")
                storage.accept(host, sample)
            except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
                return self.reply(400, {"error": str(exc)})
            self.reply(200, {"ok": True})

    return Handler


def serve(args):
    tokens = json.loads(Path(args.tokens_file).read_text(encoding="utf-8"))
    if set(tokens) != set(HOSTS) or not all(
        isinstance(tokens[h], str) and len(tokens[h]) >= 32 for h in HOSTS
    ):
        raise ValueError("missing relay authentication secrets")
    server = ThreadingHTTPServer((args.bind, args.port),
                                 make_handler(tokens, Storage()))
    server.daemon_threads = True
    print("GPU read-only telemetry relay listening", args.bind, args.port, flush=True)
    try:
        server.serve_forever(poll_interval=0.5)
    finally:
        server.server_close()


def send_sample(host, endpoint, token, timeout=8):
    sample = {"host": host, "sampled_at": time.time(), "gpus": probe()}
    body = json.dumps(sample, separators=(",", ":")).encode("utf-8")
    stamp = str(int(time.time()))
    sig = hmac.new(token.encode(), stamp.encode() + b"." + body,
                   hashlib.sha256).hexdigest()
    url = endpoint.rstrip("/") + "/api/v1/ingest/" + host
    req = request.Request(
        url, data=body, method="POST",
        headers={"Content-Type": "application/json",
                 "X-Monitor-Timestamp": stamp,
                 "X-Monitor-Signature": sig})
    with request.urlopen(req, timeout=timeout) as response:
        if response.status != 200:
            raise RuntimeError("relay did not accept sample")
    return sample


def collect(args):
    token = Path(args.token_file).read_text(encoding="utf-8").strip()
    if len(token) < 32:
        raise ValueError("missing collector authentication secret")
    failures = 0
    while True:
        start = time.monotonic()
        try:
            sample = send_sample(args.host, args.endpoint, token)
            if failures:
                print(args.host, "telemetry recovered", flush=True)
            failures = 0
            if args.once:
                print(json.dumps({"host": args.host, "gpu_count": len(sample["gpus"]),
                                  "sent_at": sample["sampled_at"]}))
                break
        except (RuntimeError, OSError, subprocess.SubprocessError, error.URLError) as exc:
            failures += 1
            if failures <= 3 or failures % 30 == 0 or args.once:
                print(args.host, "collection failed:", str(exc)[:180], flush=True)
            if args.once:
                raise
        time.sleep(max(0.2, args.interval - (time.monotonic() - start)))


def main():
    parser = argparse.ArgumentParser(description="GPU monitoring relay + collectors")
    commands = parser.add_subparsers(dest="command", required=True)
    server = commands.add_parser("serve")
    server.add_argument("--bind", default="127.0.0.1")
    server.add_argument("--port", type=int, default=18763)
    server.add_argument("--tokens-file", required=True)
    client = commands.add_parser("collect")
    client.add_argument("--host", choices=HOSTS, required=True)
    client.add_argument("--endpoint", required=True)
    client.add_argument("--token-file", required=True)
    client.add_argument("--interval", type=float, default=10)
    client.add_argument("--once", action="store_true")
    args = parser.parse_args()
    if args.command == "serve":
        serve(args)
    else:
        collect(args)


if __name__ == "__main__":
    main()
