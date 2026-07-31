```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    matches = ancilla_qubits[:6]
    flag = ancilla_qubits[6]

    # Compute whether each length-3 window equals 111.
    for offset, target in enumerate(matches):
        qc.ccx(problem_qubits[offset],
               problem_qubits[offset + 1],
               target)
        qc.ccx(target,
               problem_qubits[offset + 2],
               target)

    # flag = OR(matches), then phase-kick and uncompute.
    qc.mcx(matches, flag)
    qc.z(flag)
    qc.mcx(matches, flag)

    # Uncompute the window matches.
    for offset, target in reversed(list(enumerate(matches))):
        qc.ccx(target,
               problem_qubits[offset + 2],
               target)
        qc.ccx(problem_qubits[offset],
               problem_qubits[offset + 1],
               target)
```
