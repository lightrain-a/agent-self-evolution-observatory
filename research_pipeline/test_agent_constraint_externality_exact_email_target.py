from __future__ import annotations

import json
import sqlite3
import unittest

from research_pipeline.agent_constraint_externality_appworld_runtime import (
    _evaluate_exact_email_target,
)


def connection() -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE users (id INTEGER, email TEXT)")
    con.execute("CREATE TABLE emails (id INTEGER, sender_id INTEGER, recipient_ids TEXT, subject TEXT, body TEXT)")
    con.execute("CREATE TABLE attachments (email_id INTEGER, file_name TEXT, file_content TEXT)")
    con.execute("INSERT INTO users VALUES (?, ?)", (7, "receiver@example.com"))
    return con


def constraint() -> dict:
    return {
        "role": "TARGET",
        "evaluator_binding": {
            "app": "gmail",
            "table": "emails",
            "where": {"sender_id": 99, "subject": "subject-x"},
            "expected_fields": {},
            "expected_count": 1,
            "semantic_kind": "EMAIL_EXACT_RECIPIENT_BODY_ATTACHMENTS_V1",
            "semantic_expected": {
                "recipient": "receiver@example.com",
                "subject": "subject-x",
                "body": "body-x",
                "attachment_contents": {"a.txt": "AAA", "b.txt": "BBB"},
            },
        },
    }


class ExactEmailTargetTest(unittest.TestCase):
    def exact(self, con: sqlite3.Connection) -> bool:
        return _evaluate_exact_email_target(constraint=constraint(), connections={"gmail": con})

    def test_accepts_exact_email(self) -> None:
        con = connection()
        con.execute("INSERT INTO emails VALUES (1,99,?,?,?)", (json.dumps([7]), "subject-x", "body-x"))
        con.executemany("INSERT INTO attachments VALUES (?,?,?)", [(1,"a.txt","AAA"),(1,"b.txt","BBB")])
        self.assertTrue(self.exact(con))

    def test_rejects_wrong_recipient(self) -> None:
        con = connection()
        con.execute("INSERT INTO emails VALUES (1,99,?,?,?)", (json.dumps([8]), "subject-x", "body-x"))
        con.executemany("INSERT INTO attachments VALUES (?,?,?)", [(1,"a.txt","AAA"),(1,"b.txt","BBB")])
        self.assertFalse(self.exact(con))

    def test_rejects_wrong_body(self) -> None:
        con = connection()
        con.execute("INSERT INTO emails VALUES (1,99,?,?,?)", (json.dumps([7]), "subject-x", "wrong"))
        con.executemany("INSERT INTO attachments VALUES (?,?,?)", [(1,"a.txt","AAA"),(1,"b.txt","BBB")])
        self.assertFalse(self.exact(con))

    def test_rejects_wrong_attachment_bytes(self) -> None:
        con = connection()
        con.execute("INSERT INTO emails VALUES (1,99,?,?,?)", (json.dumps([7]), "subject-x", "body-x"))
        con.executemany("INSERT INTO attachments VALUES (?,?,?)", [(1,"a.txt","AAA"),(1,"b.txt","WRONG")])
        self.assertFalse(self.exact(con))

    def test_rejects_duplicate_matching_email(self) -> None:
        con = connection()
        for email_id in (1, 2):
            con.execute("INSERT INTO emails VALUES (?,99,?,?,?)", (email_id,json.dumps([7]),"subject-x","body-x"))
        self.assertFalse(self.exact(con))


if __name__ == "__main__":
    unittest.main()
