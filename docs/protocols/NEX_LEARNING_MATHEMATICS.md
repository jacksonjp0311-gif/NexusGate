# NEX Learning Mathematics

Teaching quality uses both a gate and rank score:

```text
Q_gate = min(P,V,A,S,H,R)
Q_rank = (P*V*A*S*H*R)^(1/6)
```

Use `Q_gate` for promotion gates and `Q_rank` only for ranking. A zero required component blocks promotion.

Damped diffusion:

```text
P = D^-1 G
a(k+1) = (1-d)s + dPa(k)
```

With `d=0.82`, the update is a contraction and the 20-iteration residual bound is about `0.82^20`.
