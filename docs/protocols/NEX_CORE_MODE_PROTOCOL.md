# NEX CORE Mode Protocol

NEX CORE routes desktop chat through `nexus:askNexCore` and `python -m nexus_gate.nex_core.cli chat`.

Required invariants:

- no `nn_router.compile`;
- no Ollama requirement;
- no external model endpoint;
- fixed Python module arguments;
- prompt length limit;
- JSON response verification;
- recommendation-only authority boundary.

NEX CORE responses expose grounding, uncertainty, organs consulted, selected route, blocked claims, and learning state. They do not expose hidden chain-of-thought or command authority.
