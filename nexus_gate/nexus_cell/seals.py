from __future__ import annotations
import hashlib
def seal_id(origin_image_id: str, cell_id: str, state_digest: str, policy_hash: str, created_at: str)->str: return hashlib.sha256((origin_image_id+cell_id+state_digest+policy_hash+created_at).encode("utf-8")).hexdigest()
def build_return_seal(*, cell_id: str, origin_image_id: str, backend: str, state_digest: str, created_at: str, policy_hash: str):
    restore_available=backend in {"hyperv_checkpoint","vhdx_differencing","container_layer"}
    return {"seal_id":seal_id(origin_image_id,cell_id,state_digest,policy_hash,created_at),"cell_id":cell_id,"origin_image_id":origin_image_id,"backend":backend,"state_digest":state_digest,"created_at":created_at,"restore_available":restore_available,"claim_boundary":"If backend = hash_only, NexusCell may claim evidence of state, not rollback. Only checkpoint-capable backends may claim restoration."}
