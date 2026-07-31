```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, vertex_qubits, ancilla_qubits):
    edges = [(0, 2), (1, 2), (1, 3), (1, 4), (3, 4)]

    def compute_equal(a, b, flag):
        for bits in ((0, 0), (0, 1), (1, 0), (1, 1)):
            for qubit, bit in ((a[0], bits[0]), (a[1], bits[1]),
                               (b[0], bits[0]), (b[1], bits[1])):
                if bit == 0:
                    qc.x(qubit)
            qc.ccx(a[0], a[1], flag)
            qc.ccx(b[0], b[1], flag)
            qc.ccx(a[0], a[1], flag)
            for qubit, bit in ((b[1], bits[1]), (b[0], bits[0]),
                               (a[1], bits[1]), (a[0], bits[0])):
                if bit == 0:
                    qc.x(qubit)

    for (u, v), flag in zip(edges, ancilla_qubits):
        compute_equal(vertex_qubits[2 * u:2 * u + 2],
                      vertex_qubits[2 * v:2 * v + 2], flag)

    for flag in ancilla_qubits:
        qc.x(flag)
    qc.h(ancilla_qubits[-1])
    qc.mcx(ancilla_qubits[:-1], ancilla_qubits[-1])
    qc.h(ancilla_qubits[-1])
    for flag in reversed(ancilla_qubits):
        qc.x(flag)

    for (u, v), flag in reversed(list(zip(edges, ancilla_qubits))):
        compute_equal(vertex_qubits[2 * u:2 * u + 2],
                      vertex_qubits[2 * v:2 * v + 2], flag)
```
