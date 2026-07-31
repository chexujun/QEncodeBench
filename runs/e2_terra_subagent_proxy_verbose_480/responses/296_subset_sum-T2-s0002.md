```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    acc = ancilla_qubits[:5]
    operations = []

    def apply_x(controls, target):
        if len(controls) == 1:
            qc.cx(controls[0], target)
        else:
            qc.mcx(controls, target)

    def controlled_add(control, value):
        # Reversibly add a known constant when `control` is 1.
        for bit in range(5):
            if (value >> bit) & 1:
                for target_bit in range(4, bit, -1):
                    controls = [control] + acc[bit:target_bit]
                    apply_x(controls, acc[target_bit])
                    operations.append((controls, acc[target_bit]))
                apply_x([control], acc[bit])
                operations.append(([control], acc[bit]))

    for control, value in zip(problem_qubits, (6, 10, 8, 3)):
        controlled_add(control, value)

    # Apply a phase precisely when the accumulator equals 14 (01110).
    qc.x(acc[0])
    qc.x(acc[4])
    qc.h(acc[4])
    qc.mcx(acc[:4], acc[4])
    qc.h(acc[4])
    qc.x(acc[4])
    qc.x(acc[0])

    # Undo the controlled additions, returning every ancilla to |0>.
    for controls, target in reversed(operations):
        apply_x(controls, target)
```
