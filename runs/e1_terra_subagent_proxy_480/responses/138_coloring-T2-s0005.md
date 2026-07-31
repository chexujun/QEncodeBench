```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, qubits, ancillas):
    data = list(qubits)
    flags = list(ancillas[:5])
    phase = ancillas[5]
    edges = [(0, 1), (0, 3), (1, 2), (1, 3), (3, 4)]

    def toggle_equal(a_low, a_high, b_low, b_high, target):
        # 00 and 11 both represent color 0; 01 and 10 represent colors 1 and 2.
        equal_patterns = [
            (0, 0, 0, 0), (0, 0, 1, 1),
            (1, 1, 0, 0), (1, 1, 1, 1),
            (0, 1, 0, 1), (1, 0, 1, 0),
        ]
        controls = [a_low, a_high, b_low, b_high]
        for pattern in equal_patterns:
            for control, bit in zip(controls, pattern):
                if bit == 0:
                    qc.x(control)
            qc.mcx(controls, target)
            for control, bit in zip(controls, pattern):
                if bit == 0:
                    qc.x(control)

    for (u, v), flag in zip(edges, flags):
        toggle_equal(data[2 * u], data[2 * u + 1], data[2 * v], data[2 * v + 1], flag)

    qc.x(phase)
    qc.h(phase)
    qc.x(flags)
    qc.mcx(flags, phase)
    qc.x(flags)
    qc.h(phase)
    qc.x(phase)

    for (u, v), flag in reversed(list(zip(edges, flags))):
        toggle_equal(data[2 * u], data[2 * u + 1], data[2 * v], data[2 * v + 1], flag)
```
