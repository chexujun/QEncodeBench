from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [13, 4, 9, 15, 4]
    target = 32
    sum_qubits = ancilla_qubits[:6]
    
    # Compute sum using controlled additions
    for idx, val in enumerate(a):
        add_controlled_value(qc, problem_qubits[idx], val, sum_qubits)
    
    # Apply phase if sum == 32
    apply_phase_if_equal(qc, sum_qubits, 32)
    
    # Uncompute sum (reverse order)
    for idx in range(len(a) - 1, -1, -1):
        add_controlled_value(qc, problem_qubits[idx], a[idx], sum_qubits)

def add_controlled_value(qc, control, value, qubits):
    """Add value to qubits if control = 1, using ripple-carry addition."""
    n = len(qubits)
    bits = [(value >> i) & 1 for i in range(n)]
    
    # Step 1: XOR all value bits into sum qubits
    for i in range(n):
        if bits[i]:
            qc.cx(control, qubits[i])
    
    # Step 2: Propagate carries using Toffoli gates
    for i in range(n - 1):
        if bits[i]:
            for j in range(i + 1, n):
                # Flip qubits[j] if control = 1 and old_qubits[i] = 1
                # After CX: new_qubits[i] = old_qubits[i] XOR control
                # So old_qubits[i] = 1 iff new_qubits[i] XOR control = 1
                # When control = 1: old_qubits[i] = 1 iff new_qubits[i] = 0
                # Use X to temporarily restore old value for Toffoli
                qc.x(qubits[i])
                qc.toffoli(control, qubits[i], qubits[j])
                qc.x(qubits[i])

def apply_phase_if_equal(qc, qubits, target):
    """Apply phase -1 if qubits encode target value."""
    n = len(qubits)
    bits = [(target >> i) & 1 for i in range(n)]
    
    # Flip all bits that should be 0 (target = 32 = 0b100000)
    for i in range(n):
        if bits[i] == 0:
            qc.x(qubits[i])
    
    # Apply multi-controlled Z gate: Z iff all qubits are 1
    # Decompose as: H on target, mcx on controls, H on target
    qc.h(qubits[-1])
    qc.mcx(list(qubits[:-1]), qubits[-1])
    qc.h(qubits[-1])
    
    # Flip bits back to original state
    for i in range(n):
        if bits[i] == 0:
            qc.x(qubits[i])
