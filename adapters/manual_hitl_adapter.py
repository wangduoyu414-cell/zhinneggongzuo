from __future__ import annotations

import hashlib
from pathlib import Path
from typing import TypedDict

from core.file_io import atomic_write_text, read_text
from ports.hitl_port import HitlPort, HitlReceiveResult

RESPONSE_FINGERPRINT_FILENAME = "hitl_response.sha256"


class HitlIngestResult(HitlReceiveResult, total=False):
    ingested: bool


class ManualHitlAdapter(HitlPort):
    def emit_prompt(self, hitl_prompt_path: Path) -> Path:
        path = Path(hitl_prompt_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.stat().st_size > 0:
            return path
        atomic_write_text(
            path,
            (
                "# HITL Prompt\n\n"
                "1. Copy the task prompt to your web UI.\n"
                "2. Run manually and copy the full response.\n"
                "3. Save response into hitl_response.md.\n"
            ),
            encoding="utf-8",
        )
        return path

    def receive_response(self, hitl_prompt_path: Path) -> HitlReceiveResult:
        prompt = Path(hitl_prompt_path)
        response_path = prompt.with_name("hitl_response.md")
        received = response_path.exists() and response_path.stat().st_size > 0
        return {"hitl_response_path": str(response_path), "received": bool(received)}

    def ingest_response(self, hitl_prompt_path: Path, text: str) -> HitlIngestResult:
        prompt = Path(hitl_prompt_path)
        response_path = prompt.with_name("hitl_response.md")
        fingerprint_path = prompt.with_name(RESPONSE_FINGERPRINT_FILENAME)
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()

        if response_path.exists() and fingerprint_path.exists():
            old_digest = read_text(fingerprint_path, encoding="utf-8").strip()
            if old_digest == digest:
                return {
                    "hitl_response_path": str(response_path),
                    "received": True,
                    "ingested": False,
                }

        atomic_write_text(response_path, text, encoding="utf-8")
        atomic_write_text(fingerprint_path, digest, encoding="utf-8")
        return {
            "hitl_response_path": str(response_path),
            "received": True,
            "ingested": True,
        }
