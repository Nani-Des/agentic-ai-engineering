"""
Tamper-evident audit log for agents (hash chain).

Each record stores the SHA-256 hash of (previous hash + this record). Change, delete or reorder any
line and every hash after it stops matching, so verify() points at the first tampered line.

For production: also ship logs to write-once storage (WORM bucket / SIEM) and sign the latest hash
periodically, so an attacker with file access cannot simply rebuild the whole chain.
"""
import hashlib
import json
from datetime import datetime, timezone
from typing import List, Optional

GENESIS = "0" * 64


def _digest(prev_hash: str, record: dict) -> str:
    body = {k: v for k, v in record.items() if k not in ("hash", "prev_hash")}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256((prev_hash + canonical).encode("utf-8")).hexdigest()


class AuditLog:
    def __init__(self, path: str):
        self.path = path
        self.last_hash = GENESIS
        try:
            with open(path, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        self.last_hash = json.loads(line)["hash"]
        except FileNotFoundError:
            pass

    def append(self, event: str, ts: Optional[str] = None, **data) -> dict:
        rec = {"ts": ts or datetime.now(timezone.utc).isoformat(), "event": event, **data}
        rec["prev_hash"] = self.last_hash
        rec["hash"] = _digest(self.last_hash, rec)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        self.last_hash = rec["hash"]
        return rec


def load(path: str) -> List[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def verify(path: str) -> dict:
    """Return {"ok": True} or the first line where the chain breaks and why."""
    prev = GENESIS
    records = load(path)
    for i, rec in enumerate(records, start=1):
        if rec.get("prev_hash") != prev:
            return {"ok": False, "line": i, "reason": "prev_hash does not match previous record (deleted or reordered?)"}
        if _digest(prev, rec) != rec.get("hash"):
            return {"ok": False, "line": i, "reason": "content changed after it was written", "record": rec}
        prev = rec["hash"]
    return {"ok": True, "records": len(records)}
