from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable
from typing import Any

from .b3_minteval_support import score_factorial_outcome

_WORD_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.'-]*", re.UNICODE)
_STOP = {
    "a","an","and","article","according","before","does","edit","edits","for","from","how","in","is",
    "latest","name","of","on","the","to","use","uses","version","what","which","with","according","revision",
    "ago","back","most","recent","state","states","time","times","did","was","were","its","it","this","that",
}


def _terms(question: str) -> list[str]:
    terms=[]
    seen=set()
    for token in _WORD_RE.findall(question.lower()):
        token=token.strip(".'-")
        if len(token)<3 or token in _STOP or token.isdigit() or token in seen:
            continue
        seen.add(token); terms.append(token)
    return terms


def _score(text: str, terms: list[str]) -> tuple[int,int]:
    low=text.lower()
    unique=sum(term in low for term in terms)
    total=sum(low.count(term) for term in terms)
    return unique,total


def _best_excerpt(text: str, terms: list[str], *, width: int = 1200) -> dict[str, Any]:
    text=str(text or "")
    if not text:
        return {"text":"","start":0,"end":0,"term_unique":0,"term_total":0}
    if len(text)<=width:
        u,t=_score(text,terms)
        return {"text":text,"start":0,"end":len(text),"term_unique":u,"term_total":t}
    low=text.lower(); centers=[]
    for term in terms:
        start=0
        while True:
            pos=low.find(term,start)
            if pos<0: break
            centers.append(pos+len(term)//2); start=pos+max(1,len(term))
    if not centers:
        centers=[len(text)//2]
    best=None
    for center in centers:
        start=max(0,min(len(text)-width,center-width//2)); end=min(len(text),start+width)
        excerpt=text[start:end]; u,t=_score(excerpt,terms)
        key=(u,t,-start)
        if best is None or key>best[0]: best=(key,{"text":excerpt,"start":start,"end":end,"term_unique":u,"term_total":t})
    return best[1]


def _normalized_excerpt(text: str) -> str:
    return " ".join(_WORD_RE.findall(str(text or "").lower()))


def _char_blocks(text: str, width: int) -> list[dict[str, Any]]:
    text=str(text or "")
    if not text: return []
    step=max(200,width)
    out=[]
    for start in range(0,len(text),step):
        end=min(len(text),start+width)
        if end-start<80: continue
        out.append({"text":text[start:end],"start":start,"end":end})
    return out


def _neutral_excerpt(text: str, terms: list[str], *, target_len: int, avoid: list[tuple[int,int]]) -> dict[str, Any] | None:
    width=max(300,min(1400,int(target_len or 800)))
    candidates=[]
    for block in _char_blocks(text,width):
        start,end=block["start"],block["end"]
        overlap=any(max(start,a)<min(end,b) for a,b in avoid)
        if overlap: continue
        u,t=_score(block["text"],terms)
        candidates.append(((u,t,abs(len(block["text"])-target_len),start),block))
    if not candidates: return None
    _,best=min(candidates,key=lambda x:x[0])
    u,t=_score(best["text"],terms)
    return {**best,"term_unique":u,"term_total":t}


def _candidate_id(article: str, question_index: int, target_index: int) -> str:
    raw=f"MINTEval/wiki_revisions/{article}/{question_index}/{target_index}".encode()
    return "b3-wiki-"+hashlib.sha256(raw).hexdigest()[:16]


def _revision_record(context: dict[str,Any], index: int, excerpt: dict[str,Any]) -> dict[str,Any]:
    return {
        "index":index,
        "timestamp":str((context or {}).get("timestamp") or ""),
        "start":int(excerpt.get("start") or 0),
        "end":int(excerpt.get("end") or 0),
        "term_unique":int(excerpt.get("term_unique") or 0),
        "term_total":int(excerpt.get("term_total") or 0),
        "text":str(excerpt.get("text") or ""),
    }


def _changed_relevant_revisions(contexts: list[dict[str,Any]], target_index: int, terms: list[str], target_excerpt: dict[str,Any]) -> list[dict[str,Any]]:
    target_norm=_normalized_excerpt(target_excerpt.get("text") or "")
    rows=[]
    for idx,ctx in enumerate(contexts):
        if idx==target_index: continue
        ex=_best_excerpt(str((ctx or {}).get("content") or ""),terms)
        norm=_normalized_excerpt(ex["text"])
        if not norm or norm==target_norm or int(ex.get("term_unique") or 0)<1: continue
        # Prefer revisions close to the requested target while still carrying query-relevant changed content.
        rows.append({"index":idx,"distance":abs(idx-target_index),"excerpt":ex,"context":ctx})
    rows.sort(key=lambda r:(-int(r["excerpt"].get("term_unique") or 0),-int(r["excerpt"].get("term_total") or 0),int(r["distance"]),int(r["index"])))
    return rows


def build_wiki_history_candidates(rows: Iterable[dict[str,Any]]) -> list[dict[str,Any]]:
    """Outcome-blind matched version-conflict candidates for MINTEval Wiki history questions.

    The target revision is fixed only by n_steps_back. No model output and no gold answer is used to choose
    S/A/B/N1/N2. S is a query-relevant excerpt from the requested revision. A/B are two distinct query-relevant
    excerpts from different revisions whose excerpt text differs from S. N1/N2 are low-query-overlap excerpts
    from the requested revision, length matched to A/B. All four arms have exactly three records.
    """
    out=[]
    for wrapped in rows:
        row=wrapped.get("row") if isinstance(wrapped,dict) and isinstance(wrapped.get("row"),dict) else wrapped
        if not isinstance(row,dict): continue
        article=str(row.get("id") or "").strip(); contexts=list(row.get("contexts") or []); questions=list(row.get("questions") or [])
        if not article or len(contexts)<3: continue
        for qi,q in enumerate(questions):
            if not isinstance(q,dict) or str(q.get("question_type") or "")!="history": continue
            try: meta=json.loads(str(q.get("metadata") or "{}"))
            except Exception: meta={}
            n=meta.get("n_steps_back")
            if not isinstance(n,int) or n<0 or n>=len(contexts): continue
            target_index=len(contexts)-1-n
            question=str(q.get("question") or "").strip(); terms=_terms(question)
            if len(terms)<2: continue
            target_ctx=contexts[target_index]; target_text=str((target_ctx or {}).get("content") or "")
            S=_best_excerpt(target_text,terms)
            if int(S.get("term_unique") or 0)<2: continue
            changed=_changed_relevant_revisions(contexts,target_index,terms,S)
            if len(changed)<2: continue
            # Prefer different sides of the target when available; otherwise take the two best distinct revisions.
            before=next((r for r in changed if r["index"]<target_index),None)
            after=next((r for r in changed if r["index"]>target_index),None)
            if before is not None and after is not None:
                chosen=[before,after]
            else:
                chosen=changed[:2]
            if chosen[0]["index"]==chosen[1]["index"]: continue
            A_ex,B_ex=chosen[0]["excerpt"],chosen[1]["excerpt"]
            N1=_neutral_excerpt(target_text,terms,target_len=len(A_ex["text"]),avoid=[(S["start"],S["end"])])
            if N1 is None: continue
            N2=_neutral_excerpt(target_text,terms,target_len=len(B_ex["text"]),avoid=[(S["start"],S["end"]),(N1["start"],N1["end"])])
            if N2 is None: continue
            srec=_revision_record(target_ctx,target_index,S)
            arec=_revision_record(chosen[0]["context"],chosen[0]["index"],A_ex)
            brec=_revision_record(chosen[1]["context"],chosen[1]["index"],B_ex)
            n1rec=_revision_record(target_ctx,target_index,N1); n2rec=_revision_record(target_ctx,target_index,N2)
            arms={
                "none":[srec,n1rec,n2rec],
                "A":[srec,arec,n2rec],
                "B":[srec,n1rec,brec],
                "AB":[srec,arec,brec],
            }
            out.append({
                "candidate_id":_candidate_id(article,qi,target_index),
                "source":"dinobby/MINTEval","split":"wiki_revisions","history_id":article,
                "question_index":qi,"question_type":"history","question":question,
                "n_steps_back":n,"target_index":target_index,"gold_answer":str(q.get("answer") or ""),
                "query_terms":terms,"support_memory":srec,"stale_memory_A":arec,"stale_memory_B":brec,
                "neutral_memory_N1":n1rec,"neutral_memory_N2":n2rec,"arm_memories":arms,
                "selection_used_model_outputs":False,"selection_used_gold_answer":False,
                "candidate_qualified":True,"mechanism_support":False,"scientific_authority":False,
            })
    out.sort(key=lambda r:(str(r["history_id"]),int(r["question_index"]),str(r["candidate_id"])))
    return out


def select_source_disjoint_wiki_candidates(candidates: Iterable[dict[str,Any]], limit: int=24) -> list[dict[str,Any]]:
    selected=[]; seen=set()
    for row in candidates:
        hid=str(row.get("history_id") or "")
        if not hid or hid in seen: continue
        selected.append(dict(row)); seen.add(hid)
        if len(selected)>=max(0,int(limit)): break
    return selected


def build_wiki_preflight(rows: Iterable[dict[str,Any]], *, freeze_limit: int=24, required_support: int=6) -> dict[str,Any]:
    candidates=build_wiki_history_candidates(rows)
    frozen=select_source_disjoint_wiki_candidates(candidates,freeze_limit)
    return {
        "schema_version":"1.0","idea_id":"B3-CO-RETRIEVAL-INTERACTION","mode":"DATA_ONLY_WIKI_VERSION_CONFLICT_PREFLIGHT",
        "source":"dinobby/MINTEval","split":"wiki_revisions",
        "candidate_definition":"History target revision fixed by n_steps_back; S is target-revision query excerpt; A/B are changed query-relevant excerpts from different revisions; N1/N2 are target-revision low-query-overlap length-matched excerpts. Selection never consults model outputs or gold answers.",
        "factorial_arms":{"none":"S+N1+N2","A":"S+A+N2","B":"S+N1+B","AB":"S+A+B"},
        "support_rule":"Formal interaction support requires matched task correctness with a negative factorial interaction and no single-memory harm; the strongest joint-only pattern is none=1,A=1,B=1,AB=0. Ordinary single-memory harm does not qualify.",
        "candidate_pool":len(candidates),"source_disjoint_frozen":len(frozen),"required_interaction_positive_support":int(required_support),
        "selection_used_model_outputs":False,"selection_used_gold_answer":False,"frozen_candidates":frozen,
        "scientific_authority":False,"authority":{"problem_gate":False,"method":False,"experiment":False,"p0":False,"gpu":False},
    }


def score_wiki_factorial(outcomes: dict[str,Any]) -> dict[str,Any]:
    return score_factorial_outcome(outcomes)
