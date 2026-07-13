# NEX LEARN Protocol

LEARN calculates a proposal. It does not apply it.

Persistent conductance uses log-space bounded updates:

```text
z = log(g)
delta_z = clip(eta * Q * u - mu*C - nu*R - lambda*(z-z0), -delta_max, delta_max)
g' = exp(clip(z + delta_z, log(g_min), log(g_max)))
```

Defaults are versioned in code: `eta=0.04`, `delta_max=0.05`, `g_min=0.01`, `g_max=10.0`, and at least three independent verified teachings. Human authorization is mandatory before application.
