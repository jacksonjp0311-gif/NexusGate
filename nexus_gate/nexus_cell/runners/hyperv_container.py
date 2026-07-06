import shutil
from pathlib import Path
from nexus_gate.nexus_cell.runners.base import RunnerResult
def run_hyperv_container(payload: Path)->RunnerResult:
    if shutil.which("docker") is None: return RunnerResult(127,"","Docker not found; Hyper-V container runner is unavailable.","hyperv_container","Hyper-V container path exists but fails gracefully when Docker/Windows containers are unavailable.")
    return RunnerResult(64,"","Hyper-V container backend is scaffolded but not enabled by NexusCell v0.1.","hyperv_container","Scaffold only. No container execution is performed by default.")
