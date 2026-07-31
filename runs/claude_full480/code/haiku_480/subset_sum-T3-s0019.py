from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    a = [8, 13, 14, 7, 11]
    sum_qubits = ancilla_qubits[:6]
    
    # Compute: Add each element conditionally to sum register
    for i in range(5):
        controlled_add(qc, problem_qubits[i], sum_qubits, a[i])
    
    # Apply phase if sum == 11 (binary 001011)
    apply_phase_if_sum_11(qc, sum_qubits)
    
    # Uncompute: Subtract each element (reverse order)
    for i in range(4, -1, -1):
        controlled_subtract(qc, problem_qubits[i], sum_qubits, a[i])


def controlled_add(qc, control, sum_qubits, value):
    """Add value to sum when control=1 using Toffoli-based ripple carry."""
    n = len(sum_qubits)
    value_bits = [(value >> i) & 1 for i in range(n)]
    
    # Ripple-carry addition: process each bit position
    for i in range(n - 1):
        # Compute carry propagation
        qc.ccx(control, sum_qubits[i], sum_qubits[i + 1])
        # Add value bit if set
        if value_bits[i]:
            qc.cx(control, sum_qubits[i])
    
    # Handle MSB (no carry out)
    if value_bits[n - 1]:
        qc.cx(control, sum_qubits[n - 1])


def apply_phase_if_sum_11(qc, sum_qubits):
    """Apply Z phase gate if sum equals 11."""
    # 11 in binary: 001011 => bits are [1, 1, 0, 1, 0, 0]
    
    # Flip bits that should be 0 to prepare for multi-controlled gate
    qc.x(sum_qubits[2])
    qc.x(sum_qubits[4])
    qc.x(sum_qubits[5])
    
    # Apply multi-controlled phase gate (phase pi is equivalent to Z)
    # All 6 qubits must be 1 for phase to be applied
    qc.mcp(math.pi, sum_qubits, sum_qubits[0])
    
    # Un-flip the prepared qubits
    qc.x(sum_qubits[2])
    qc.x(sum_qubits[4])
    qc.x(sum_qubits[5])


def controlled_subtract(qc, control, sum_qubits, value):
    """Subtract value from sum when control=1 (reverse of addition)."""
    n = len(sum_qubits)
    value_bits = [(value >> i) & 1 for i in range(n)]
    
    # Uncompute: reverse order of operations from controlled_add
    if value_bits[n - 1]:
        qc.cx(control, sum_qubits[n - 1])
    
    for i in range(n - 2, -1, -1):
        if value_bits[i]:
            qc.cx(control, sum_qubits[i])
        qc.ccx(control, sum_qubits[i], sum_qubits[i + 1])
