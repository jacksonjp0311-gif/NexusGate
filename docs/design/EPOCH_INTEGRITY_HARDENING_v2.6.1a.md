# Epoch Integrity Hardening v2.6.1a

NEXUS separates content identity from observation.

Source Epoch identity is derived from canonical source content, runtime contract version, and schema compatibility. It does not include the previous epoch ID, so repeated runs against unchanged source reuse the same Source Epoch.

Observation Events are repeatable measurements against a Source Epoch. They record generation time, gate report hashes, dirty state, runtime state, producer version, and hash-chain links.

Law: repeated execution is not a new epoch.

Working-tree captures may orient a local run, but they are `working_tree_only` and are not durable learning parents.

Claim boundary: epoch hardening is local temporal identity evidence only. It does not prove correctness, safety, security, production readiness, model understanding, consciousness, or autonomous authority.
