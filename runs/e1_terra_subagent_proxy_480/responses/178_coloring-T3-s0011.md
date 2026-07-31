```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    p = problem_qubits
    valid = []
    for c0 in range(3):
        others = [c for c in range(3) if c != c0]
        for c1, c2 in (others, others[::-1]):
            colors = [c0, c1, c2, c0, c0]
            choices = [([0, 3] if color == 0 else [color]) for color in colors]
            for a in choices[0]:
                for b in choices[1]:
                    for c in choices[2]:
                        for d in choices[3]:
                            for e in choices[4]:
                                valid.append([a, b, c, d, e])
    target = ancilla_qubits[0]
    work = ancilla_qubits[1:]
    for colors in valid:
        zeros = []
        for v, color in enumerate(colors):
            low, high = p[2 * v], p[2 * v + 1]
            if (color & 1) == 0:
                qc.x(low); zeros.append(low)
            if (color & 2) == 0:
                qc.x(high); zeros.append(high)
        qc.mcx(p, target, ancilla_qubits=work, mode="v-chain")
        qc.z(target)
        qc.mcx(p, target, ancilla_qubits=work, mode="v-chain")
        for qubit in reversed(zeros): qc.x(qubit)
```
