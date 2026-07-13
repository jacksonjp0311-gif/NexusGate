from __future__ import annotations


def solve_linear(matrix: list[list[float]], rhs: list[float]) -> list[float]:
    n = len(rhs)
    a = [row[:] + [rhs[i]] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(a[r][col]))
        if abs(a[pivot][col]) < 1e-12:
            raise ValueError("singular_laplacian")
        a[col], a[pivot] = a[pivot], a[col]
        factor = a[col][col]
        a[col] = [value / factor for value in a[col]]
        for row in range(n):
            if row == col:
                continue
            scale = a[row][col]
            if scale:
                a[row] = [a[row][i] - scale * a[col][i] for i in range(n + 1)]
    return [a[i][-1] for i in range(n)]


def electrical_flow(nodes: list[str], edges: list[dict], source: str, sink: str) -> dict:
    if source not in nodes or sink not in nodes:
        raise ValueError("source_or_sink_missing")
    index = {node: i for i, node in enumerate(nodes)}
    grounded = sink
    active = [node for node in nodes if node != grounded]
    active_index = {node: i for i, node in enumerate(active)}
    n = len(active)
    matrix = [[0.0 for _ in range(n)] for _ in range(n)]
    rhs = [0.0 for _ in range(n)]
    rhs[active_index[source]] = 1.0
    for edge in edges:
        u = edge["source"]
        v = edge["target"]
        d = float(edge["conductance"])
        if d <= 0:
            raise ValueError("non_positive_conductance")
        if u != grounded:
            matrix[active_index[u]][active_index[u]] += d
        if v != grounded:
            matrix[active_index[v]][active_index[v]] += d
        if u != grounded and v != grounded:
            matrix[active_index[u]][active_index[v]] -= d
            matrix[active_index[v]][active_index[u]] -= d
    potentials = {grounded: 0.0}
    solution = solve_linear(matrix, rhs)
    for node, value in zip(active, solution):
        potentials[node] = value
    flows = []
    for edge in edges:
        flow = float(edge["conductance"]) * (potentials[edge["source"]] - potentials[edge["target"]])
        flows.append({**edge, "flow": round(flow, 6), "abs_flow": round(abs(flow), 6)})
    return {
        "node_potentials": {node: round(potentials[node], 6) for node in nodes},
        "edge_flows": flows,
        "effective_resistance": round(potentials[source] - potentials[sink], 6),
    }
