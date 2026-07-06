from pathlib import Path
from nexus_gate.nexus_cell.runners.base import NexusCellRunner, RunnerResult
from nexus_gate.nexus_cell.secrets.redaction import redact_text
class MockRunner(NexusCellRunner):
    name="mock"
    def run(self, payload_path: Path)->RunnerResult:
        path=Path(payload_path)
        if not path.exists(): return RunnerResult(2,"",f"payload not found: {path}","mock","Mock runner does not execute payloads; it reads and hashes local payload metadata only.")
        text=path.read_text(encoding="utf-8-sig"); safe=redact_text(text)
        stdout=f"NexusCell mock runner accepted payload: {path.name}\nbytes={len(text.encode('utf-8'))}\npreview={safe[:120]}"
        return RunnerResult(0,stdout,"","mock","Mock runner does not execute payloads; it reads and hashes local payload metadata only.")
