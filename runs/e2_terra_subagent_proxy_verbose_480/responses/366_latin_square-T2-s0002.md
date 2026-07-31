```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    a0, a1, a2, a3, a4 = ancilla_qubits[:5]

    # Cell (0,0) must decode to 0: its two code bits must be equal.
    qc.cx(problem_qubits[0], a0)
    qc.cx(problem_qubits[1], a0)
    qc.x(a0)

    # Cells (1,2) and (2,0) must decode to 2: low=0, high=1.
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[4])

    controls = [a0, problem_qubits[2], problem_qubits[3],
                problem_qubits[4], problem_qubits[5]]
    qc.mcx(controls, a1, ancilla_qubits=[a2, a3, a4], mode="v-chain")
    qc.z(a1)
    qc.mcx(controls, a1, ancilla_qubits=[a2, a3, a4], mode="v-chain")

    qc.x(problem_qubits[4])
    qc.x(problem_qubits[2])

    qc.x(a0)
    qc.cx(problem_qubits[1], a0)
    qc.cx(problem_qubits[0], a0)
```
