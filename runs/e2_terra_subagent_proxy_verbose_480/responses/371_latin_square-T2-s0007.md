```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    a0, a1, b0, b1, c0, c1 = problem_qubits
    equality_flag = ancilla_qubits[0]
    phase_flag = ancilla_qubits[1]
    work = ancilla_qubits[2:5]

    qc.x(equality_flag)
    qc.cx(a0, equality_flag)
    qc.cx(a1, equality_flag)

    qc.x(b0)
    qc.x(c1)

    controls = [equality_flag, b0, b1, c0, c1]
    qc.mcx(controls, phase_flag, ancilla_qubits=work, mode="v-chain")
    qc.z(phase_flag)
    qc.mcx(controls, phase_flag, ancilla_qubits=work, mode="v-chain")

    qc.x(c1)
    qc.x(b0)

    qc.cx(a1, equality_flag)
    qc.cx(a0, equality_flag)
    qc.x(equality_flag)
```
