```python
import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    e0, e1, e2 = ancilla_qubits[:3]

    def compute_same_color(a_lo, a_hi, b_lo, b_hi, target):
        # Convert b into the bitwise XOR of the two original codewords.
        qc.cx(a_lo, b_lo)
        qc.cx(a_hi, b_hi)

        # Equal raw codewords: (a_lo == b_lo) and (a_hi == b_hi).
        qc.x(b_lo)
        qc.x(b_hi)
        qc.ccx(b_lo, b_hi, target)
        qc.x(b_hi)
        qc.x(b_lo)

        # The additional equal-color cases are 00 <-> 11.
        # With b holding a XOR b, these have b == 11 and a_lo == a_hi.
        qc.cx(a_lo, a_hi)
        qc.x(a_hi)
        qc.mcx([b_lo, b_hi, a_hi], target)
        qc.x(a_hi)
        qc.cx(a_lo, a_hi)

        # Restore the original codeword bits.
        qc.cx(a_hi, b_hi)
        qc.cx(a_lo, b_lo)

    # Compute whether each edge is monochromatic.
    compute_same_color(problem_qubits[0], problem_qubits[1],
                       problem_qubits[4], problem_qubits[5], e0)
    compute_same_color(problem_qubits[2], problem_qubits[3],
                       problem_qubits[4], problem_qubits[5], e1)
    compute_same_color(problem_qubits[6], problem_qubits[7],
                       problem_qubits[8], problem_qubits[9], e2)

    # Mark precisely when no edge is monochromatic.
    qc.x(e0)
    qc.x(e1)
    qc.x(e2)
    qc.mcp(math.pi, [e0, e1], e2)
    qc.x(e2)
    qc.x(e1)
    qc.x(e0)

    # Uncompute edge predicates.
    compute_same_color(problem_qubits[6], problem_qubits[7],
                       problem_qubits[8], problem_qubits[9], e2)
    compute_same_color(problem_qubits[2], problem_qubits[3],
                       problem_qubits[4], problem_qubits[5], e1)
    compute_same_color(problem_qubits[0], problem_qubits[1],
                       problem_qubits[4], problem_qubits[5], e0)
```
