```python
import math
from itertools import permutations, product

from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Decoded colors: 0 is represented by 00 or 11, 1 by 01, 2 by 10.
    code_patterns = ((0, 3), (1,), (2,))

    def apply_minterm(target, wires, bits):
        """Toggle target iff the listed wires have exactly the given bits."""
        zero_wires = [wire for wire, bit in zip(wires, bits) if bit == 0]
        for wire in zero_wires:
            qc.x(wire)
        qc.mcx(wires, target, mode="noancilla")
        for wire in reversed(zero_wires):
            qc.x(wire)

    def decoded_equal_patterns(vertex_a, vertex_b):
        wires = [
            problem_qubits[2 * vertex_a],
            problem_qubits[2 * vertex_a + 1],
            problem_qubits[2 * vertex_b],
            problem_qubits[2 * vertex_b + 1],
        ]
        patterns = []
        for color in range(3):
            for code_a, code_b in product(code_patterns[color], repeat=2):
                patterns.append((
                    wires,
                    (
                        code_a & 1, (code_a >> 1) & 1,
                        code_b & 1, (code_b >> 1) & 1,
                    ),
                ))
        return patterns

    def decoded_unequal_patterns(vertex_a, vertex_b):
        wires = [
            problem_qubits[2 * vertex_a],
            problem_qubits[2 * vertex_a + 1],
            problem_qubits[2 * vertex_b],
            problem_qubits[2 * vertex_b + 1],
        ]
        patterns = []
        for color_a in range(3):
            for color_b in range(3):
                if color_a == color_b:
                    continue
                for code_a, code_b in product(
                    code_patterns[color_a], code_patterns[color_b]
                ):
                    patterns.append((
                        wires,
                        (
                            code_a & 1, (code_a >> 1) & 1,
                            code_b & 1, (code_b >> 1) & 1,
                        ),
                    ))
        return patterns

    def all_distinct_patterns(vertices):
        wires = []
        for vertex in vertices:
            wires.extend((
                problem_qubits[2 * vertex],
                problem_qubits[2 * vertex + 1],
            ))

        patterns = []
        for colors in permutations(range(3)):
            for codes in product(*(code_patterns[color] for color in colors)):
                bits = []
                for code in codes:
                    bits.extend((code & 1, (code >> 1) & 1))
                patterns.append((wires, tuple(bits)))
        return patterns

    def apply_patterns(target, patterns):
        for wires, bits in patterns:
            apply_minterm(target, wires, bits)

    # The graph is properly colored exactly when:
    #   c0 == c3,
    #   c0, c2, c4 are all distinct,
    #   c1 != c0.
    all_distinct = ancilla_qubits[0]
    equal_03 = ancilla_qubits[1]
    unequal_10 = ancilla_qubits[2]

    distinct_024_patterns = all_distinct_patterns((0, 2, 4))
    equal_03_patterns = decoded_equal_patterns(0, 3)
    unequal_10_patterns = decoded_unequal_patterns(1, 0)

    apply_patterns(all_distinct, distinct_024_patterns)
    apply_patterns(equal_03, equal_03_patterns)
    apply_patterns(unequal_10, unequal_10_patterns)

    qc.mcp(math.pi, [all_distinct, equal_03], unequal_10)

    apply_patterns(unequal_10, reversed(unequal_10_patterns))
    apply_patterns(equal_03, reversed(equal_03_patterns))
    apply_patterns(all_distinct, reversed(distinct_024_patterns))
```
