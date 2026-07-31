```python
from qiskit.circuit.library import PhaseOracle

def build_oracle(qc, q=None, ancillas=None):
    if q is None:
        q = qc.qubits[:10]
    z = lambda a, b: f"(({a} & {b}) | (~{a} & ~{b}))"
    one = lambda a, b: f"(~{a} & {b})"
    two = lambda a, b: f"({a} & ~{b})"
    eq = lambda a, b, c, d: f"(({z(a,b)} & {z(c,d)}) | ({one(a,b)} & {one(c,d)}) | ({two(a,b)} & {two(c,d)}))"
    diff = lambda a, b, c, d: f"~{eq(a,b,c,d)}"
    e01=diff("x0","x1","x2","x3"); e02=diff("x0","x1","x4","x5"); e04=diff("x0","x1","x8","x9")
    e13=diff("x2","x3","x6","x7"); e14=diff("x2","x3","x8","x9"); e23=diff("x4","x5","x6","x7"); e34=diff("x6","x7","x8","x9")
    expression=f"({e01} & {e02} & {e04} & {e13} & {e14} & {e23} & {e34})"
    qc.compose(PhaseOracle(expression), qubits=q[:10], inplace=True)
```
