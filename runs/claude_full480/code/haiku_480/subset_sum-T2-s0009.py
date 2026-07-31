from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Subset sum oracle: marks states where selected elements sum to 12.
    a = [6, 5, 9, 6], target = 12
    """
    
    a = [6, 5, 9, 6]
    target = 12
    sum_qubits = ancilla_qubits[:5]
    
    # Compute sum: sum_qubits will contain binary representation of sum
    for i, value in enumerate(a):
        add_controlled_constant(qc, problem_qubits[i], sum_qubits, value)
    
    # Apply phase if sum == target (12 = 01100 in binary)
    # Strategy: flip bits so that target looks like all 1s, apply multi-controlled Z,
    # then unflip
    target_bits = [int(b) for b in bin(target)[2:].zfill(len(sum_qubits))[::-1]]
    
    # Flip bits where target_bits == 0
    for i in range(len(sum_qubits)):
        if target_bits[i] == 0:
            qc.x(sum_qubits[i])
    
    # Apply phase: use multi-controlled Z via CZ chain
    # Apply Z to sum_qubits[0] controlled by all others
    qc.cx(sum_qubits[1], sum_qubits[0])
    qc.cx(sum_qubits[2], sum_qubits[0])
    qc.cx(sum_qubits[3], sum_qubits[0])
    qc.cx(sum_qubits[4], sum_qubits[0])
    qc.z(sum_qubits[0])
    qc.cx(sum_qubits[4], sum_qubits[0])
    qc.cx(sum_qubits[3], sum_qubits[0])
    qc.cx(sum_qubits[2], sum_qubits[0])
    qc.cx(sum_qubits[1], sum_qubits[0])
    
    # Unflip bits
    for i in range(len(sum_qubits)):
        if target_bits[i] == 0:
            qc.x(sum_qubits[i])
    
    # Uncompute sum (reverse of the add operations)
    for i in range(len(a)-1, -1, -1):
        add_controlled_constant(qc, problem_qubits[i], sum_qubits, a[i])


def add_controlled_constant(qc, control, register, constant):
    """Add constant to register if control qubit is 1, using binary addition."""
    if constant == 0:
        return
    
    bits = bin(constant)[2:].zfill(len(register))[::-1]
    
    # Process each bit of the constant
    carry = control
    for i in range(len(register)):
        if bits[i] == '1':
            # Add bit i: compute sum and carry
            qc.cx(carry, register[i])
            if i < len(register) - 1:
                # Compute new carry
                qc.ccx(register[i], carry, register[i+1])
                qc.cx(carry, register[i])
        else:
            # Just propagate carry
            if i < len(register) - 1:
                qc.ccx(register[i], carry, register[i+1])
