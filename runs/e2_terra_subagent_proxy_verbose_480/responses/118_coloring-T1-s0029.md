```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    e01, e13, e23 = ancilla_qubits[:3]

    def equality_test(v_a, v_b, target):
        la, ha = problem_qubits[2 * v_a], problem_qubits[2 * v_a + 1]
        lb, hb = problem_qubits[2 * v_b], problem_qubits[2 * v_b + 1]

        # In the transformed representation, high=0 denotes color 0,
        # while high=1 and low selects color 1 or 2.
        qc.x(ha)
        qc.x(hb)
        qc.ccx(ha, hb, target)
        qc.x(hb)
        qc.x(ha)

        # Both vertices have color 1.
        qc.mcx([la, ha, lb, hb], target)

        # Both vertices have color 2.
        qc.x(la)
        qc.x(lb)
        qc.mcx([la, ha, lb, hb], target)
        qc.x(lb)
        qc.x(la)

    # Convert each vertex encoding so its high bit is 0 precisely for color 0.
    for v in range(4):
        qc.cx(problem_qubits[2 * v], problem_qubits[2 * v + 1])

    equality_test(0, 1, e01)
    equality_test(1, 3, e13)
    equality_test(2, 3, e23)

    # Mark when none of the three edges is monochromatic.
    qc.x(e01)
    qc.x(e13)
    qc.x(e23)
    qc.h(e23)
    qc.mcx([e01, e13], e23)
    qc.h(e23)
    qc.x(e23)
    qc.x(e13)
    qc.x(e01)

    equality_test(2, 3, e23)
    equality_test(1, 3, e13)
    equality_test(0, 1, e01)

    for v in reversed(range(4)):
        qc.cx(problem_qubits[2 * v], problem_qubits[2 * v + 1])
```
