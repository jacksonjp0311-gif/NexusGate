# NEX Message Replay Protocol

Replay starts from durable ledgers and reconstructs message, teaching, learning, and cycle state. It verifies event hashes, previous hashes, duplicate IDs, payload hashes, lifecycle order, and required stage files.

Missing required seals return warn or fail. A verifier must never compare a rebuilt value to itself and call that a pass.
