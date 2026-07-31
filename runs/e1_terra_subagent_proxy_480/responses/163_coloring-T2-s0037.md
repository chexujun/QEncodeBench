```python
from qiskit import QuantumCircuit

def build_oracle():
    qc = QuantumCircuit(18)
    edges = [(0, 1), (0, 2), (1, 2), (1, 3), (1, 4), (2, 3), (3, 4)]
    equal_color_patterns = ((0, 0, 0, 0), (0, 0, 1, 1), (1, 1, 0, 0), (1, 1, 1, 1), (0, 1, 0, 1), (1, 0, 1, 0))
    def toggle_equal_flag(bits, target):
        for pattern in equal_color_patterns:
            for bit, value in zip(bits, pattern):
                if value == 0: qc.x(bit)
            qc.mcx(bits, target)
            for bit, value in reversed(tuple(zip(bits, pattern))):
                if value == 0: qc.x(bit)
    flags = list(range(10, 17))
    for flag, (u, v) in zip(flags, edges):
        toggle_equal_flag([2 * u, 2 * u + 1, 2 * v, 2 * v + 1], flag)
    for flag in flags: qc.x(flag)
    qc.h(flags[-1]); qc.mcx(flags[:-1], flags[-1]); qc.h(flags[-1])
    for flag in reversed(flags): qc.x(flag)
    for flag, (u, v) in reversed(list(zip(flags, edges))):
        toggle_equal_flag([2 * u, 2 * u + 1, 2 * v, 2 * v + 1], flag)
    return qc
```
