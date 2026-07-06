from dataclasses import dataclass
@dataclass
class RunnerResult:
    exit_code:int
    stdout:str
    stderr:str
    backend:str
    claim_boundary:str
class NexusCellRunner:
    name="base"
    def run(self,payload_path):
        raise NotImplementedError
