```python
import math
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    # A Boolean polynomial is represented in algebraic normal form (ANF):
    # a set of monomial bitmasks, with set symmetric difference as XOR.
    def xor_poly(*polys):
        out = set()
        for poly in polys:
            for term in poly:
                if term in out:
                    out.remove(term)
                else:
                    out.add(term)
        return out

    def mul_poly(left, right):
        out = set()
        for a in left:
            for b in right:
                term = a | b
                if term in out:
                    out.remove(term)
                else:
                    out.add(term)
        return out

    one = {0}

    def var(index):
        return {1 << index}

    def color_polynomials(vertex):
        low = var(2 * vertex)
        high = var(2 * vertex + 1)
        low_high = mul_poly(low, high)

        # Decoding: 00,11 -> 0; 01 -> 1; 10 -> 2.
        color_zero = xor_poly(one, low, high)
        color_one = xor_poly(low, low_high)
        color_two = xor_poly(high, low_high)
        return color_zero, color_one, color_two

    edges = (
        (0, 1), (0, 2), (0, 4), (1, 5),
        (2, 3), (2, 4), (2, 5), (3, 5),
    )

    colors = [color_polynomials(v) for v in range(6)]

    # Form the ANF of the conjunction of all "edge endpoints differ"
    # predicates.  This is symbolic Boolean algebra, not enumeration.
    predicate = one
    for u, v in edges:
        equal = xor_poly(
            mul_poly(colors[u][0], colors[v][0]),
            mul_poly(colors[u][1], colors[v][1]),
            mul_poly(colors[u][2], colors[v][2]),
        )
        different = xor_poly(one, equal)
        predicate = mul_poly(predicate, different)

    # A -1 phase for each ANF monomial implements (-1)^predicate.
    # Ancillas are deliberately unused and therefore remain |0>.
    for monomial in predicate:
        if monomial == 0:
            # A constant phase is global and may be omitted.
            continue

        controls = [
            problem_qubits[i]
            for i in range(len(problem_qubits))
            if (monomial >> i) & 1
        ]

        if len(controls) == 1:
            qc.z(controls[0])
        elif len(controls) == 2:
            qc.cz(controls[0], controls[1])
        else:
            qc.mcp(math.pi, controls[:-1], controls[-1])
```
