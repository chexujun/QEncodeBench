from qiskit import QuantumCircuit
from math import pi

def build_oracle(qc, problem_qubits, ancilla_qubits):
    a = [9, 8, 15, 12, 5]
    target = 23
    
    sum_qubits = ancilla_qubits[:6]
    
    # Compute the sum by controlled addition
    for i, val in enumerate(a):
        controlled_add_binary(qc, problem_qubits[i], val, sum_qubits)
    
    # Apply -1 phase if sum equals target
    apply_phase_if_equal(qc, sum_qubits, target)
    
    # Uncompute: undo additions in reverse order
    for i in range(len(a) - 1, -1, -1):
        controlled_subtract_binary(qc, problem_qubits[i], a[i], sum_qubits)


def controlled_add_binary(qc, control, value, sum_qubits):
    """Add value to sum_qubits if control == 1, using ripple-carry addition."""
    n = len(sum_qubits)
    carry = control
    
    for i in range(n):
        if (value >> i) & 1:
            # XOR this bit with carry
            qc.cx(carry, sum_qubits[i])
            
            # Compute next carry using the available qubits
            if i < n - 1:
                # Use sum_qubits[i+1] as temporary for carry computation
                # Compute: carry_out = sum[i] AND carry (after XOR, this equals old_sum[i] AND carry via identity)
                qc.ccx(sum_qubits[i], carry, sum_qubits[i + 1])
                qc.cx(carry, sum_qubits[i + 1])
                carry = sum_qubits[i + 1]


def controlled_subtract_binary(qc, control, value, sum_qubits):
    """Subtract value from sum_qubits if control == 1 (reverse of add)."""
    n = len(sum_qubits)
    carry = control
    
    for i in range(n - 1, -1, -1):
        if (value >> i) & 1:
            if i < n - 1:
                # Restore previous carry
                qc.cx(carry, sum_qubits[i + 1])
                qc.ccx(sum_qubits[i], carry, sum_qubits[i + 1])
                carry = sum_qubits[i + 1]
            
            # Reverse the XOR
            qc.cx(carry, sum_qubits[i])


def apply_phase_if_equal(qc, qubits, target_value):
    """Apply -π phase to computational basis states where qubits represent target_value."""
    target_bits = [(target_value >> i) & 1 for i in range(len(qubits))]
    
    # Flip qubits where target bit is 0 (to check if ALL qubits match)
    for i, bit in enumerate(target_bits):
        if bit == 0:
            qc.x(qubits[i])
    
    # Apply multi-controlled phase gate (Z gate = phase π)
    qc.mcp(pi, qubits[:-1], qubits[-1])
    
    # Flip qubits back
    for i, bit in enumerate(target_bits):
        if bit == 0:
            qc.x(qubits[i])
