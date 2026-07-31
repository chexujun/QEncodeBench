```python
import math
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    # A polynomial is represented in algebraic normal form over GF(2):
    # a set of monomials, each monomial being a frozenset of variable indices.
    one = {frozenset()}

    def variable(index):
        return {frozenset((index,))}

    def xor_poly(*polynomials):
        result = set()
        for polynomial in polynomials:
            result ^= polynomial
        return result

    def and_poly(left, right):
        result = set()
        for left_term in left:
            for right_term in right:
                term = left_term | right_term
                if term in result:
                    result.remove(term)
                else:
                    result.add(term)
        return result

    def color_zero(low, high):
        # 00 and 11 both decode to color 0.
        return xor_poly(one, variable(low), variable(high))

    def color_one(low, high):
        # 01
        return and_poly(variable(low), xor_poly(one, variable(high)))

    def color_two(low, high):
        # 10
        return and_poly(variable(high), xor_poly(one, variable(low)))

    def equal_color(vertex_a, vertex_b):
        a0, a1 = 2 * vertex_a, 2 * vertex_a + 1
        b0, b1 = 2 * vertex_b, 2 * vertex_b + 1
        return xor_poly(
            and_poly(color_zero(a0, a1), color_zero(b0, b1)),
            and_poly(color_one(a0, a1), color_one(b0, b1)),
            and_poly(color_two(a0, a1), color_two(b0, b1)),
        )

    valid = one
    for vertex_a, vertex_b in (
        (0, 2), (0, 5), (1, 2), (1, 3),
        (1, 4), (1, 5), (3, 4),
    ):
        different = xor_poly(one, equal_color(vertex_a, vertex_b))
        valid = and_poly(valid, different)

    # Apply (-1)^valid using its algebraic normal form.  Each monomial
    # contributes a controlled phase of pi exactly when all its bits are one.
    for monomial in valid:
        qubits = [problem_qubits[index] for index in monomial]
        if len(qubits) == 1:
            qc.z(qubits[0])
        elif len(qubits) > 1:
            qc.mcp(math.pi, qubits[:-1], qubits[-1])
```
