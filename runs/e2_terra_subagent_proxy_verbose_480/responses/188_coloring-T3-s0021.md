```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a0, a1, a2, a3 = ancilla_qubits

    def mcx_pattern(controls, target, bits):
        for q, bit in zip(controls, bits):
            if bit == 0:
                qc.x(q)
        dirty = [q for q in problem_qubits if q not in controls][:2]
        qc.mcx(controls, target, ancilla_qubits=dirty, mode="v-chain-dirty")
        for q, bit in reversed(list(zip(controls, bits))):
            if bit == 0:
                qc.x(q)

    def compute_different(u, v, target):
        # Start with 1, then toggle for each equal-color code pair.
        qc.x(target)
        controls = [
            problem_qubits[2 * u],
            problem_qubits[2 * u + 1],
            problem_qubits[2 * v],
            problem_qubits[2 * v + 1],
        ]

        # Both vertices decode to color 0: codes 00 or 11.
        for left in ((0, 0), (1, 1)):
            for right in ((0, 0), (1, 1)):
                mcx_pattern(controls, target, left + right)

        # Both decode to color 1 (01), or both to color 2 (10).
        mcx_pattern(controls, target, (1, 0, 1, 0))
        mcx_pattern(controls, target, (0, 1, 0, 1))

    def compute_block(edges, target, leaves):
        for edge, leaf in zip(edges, leaves):
            compute_different(edge[0], edge[1], leaf)

        if len(leaves) == 2:
            qc.ccx(leaves[0], leaves[1], target)
        else:
            qc.mcx(leaves, target)

        for edge, leaf in reversed(list(zip(edges, leaves))):
            compute_different(edge[0], edge[1], leaf)

    block_a = [(0, 3), (0, 5), (1, 5)]
    block_b = [(2, 3), (2, 4)]
    block_c = [(2, 5), (4, 5)]

    compute_block(block_a, a0, [a1, a2, a3])
    compute_block(block_b, a1, [a2, a3])
    qc.ccx(a0, a1, a2)          # a2 = block_a AND block_b
    compute_block(block_b, a1, [a2, a3])
    compute_block(block_a, a0, [a1, a2, a3])

    compute_block(block_c, a0, [a1, a3])
    qc.cz(a2, a0)
    compute_block(block_c, a0, [a1, a3])

    qc.ccx(a0, a1, a2)
    compute_block(block_b, a1, [a2, a3])
    compute_block(block_a, a0, [a1, a2, a3])
```
