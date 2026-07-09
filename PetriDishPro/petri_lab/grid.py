from __future__ import annotations

from typing import List

Grid = List[List[float]]


def zeros(n: int, value: float = 0.0) -> Grid:
    return [[float(value) for _ in range(n)] for _ in range(n)]


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x


def diffuse(g: Grid, rate: float) -> Grid:
    n = len(g)
    out = zeros(n)
    keep = 1.0 - rate
    share = rate / 4.0
    for y in range(n):
        ym = y - 1 if y > 0 else y
        yp = y + 1 if y < n - 1 else y
        row = out[y]
        for x in range(n):
            xm = x - 1 if x > 0 else x
            xp = x + 1 if x < n - 1 else x
            row[x] = keep * g[y][x] + share * (g[ym][x] + g[yp][x] + g[y][xm] + g[y][xp])
    return out


def total(g: Grid) -> float:
    return sum(sum(row) for row in g)


def max_value(g: Grid) -> float:
    m = 0.0
    for row in g:
        for v in row:
            if v > m:
                m = v
    return m


def normalize(g: Grid) -> Grid:
    m = max_value(g)
    if m <= 0:
        return zeros(len(g))
    return [[v / m for v in row] for row in g]


def downsample(g: Grid, target: int = 64) -> Grid:
    n = len(g)
    if n <= target:
        return g
    step = n / target
    out = []
    for yy in range(target):
        y0 = int(yy * step)
        y1 = int((yy + 1) * step)
        if y1 <= y0:
            y1 = y0 + 1
        row = []
        for xx in range(target):
            x0 = int(xx * step)
            x1 = int((xx + 1) * step)
            if x1 <= x0:
                x1 = x0 + 1
            s = 0.0
            c = 0
            for y in range(y0, min(y1, n)):
                for x in range(x0, min(x1, n)):
                    s += g[y][x]
                    c += 1
            row.append(s / c if c else 0.0)
        out.append(row)
    return out
