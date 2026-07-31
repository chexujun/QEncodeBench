from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [9, 8, 2, 10]
    target = 27
    sum_reg = ancilla_qubits
    
    # Compute sum into ancilla register
    for i in range(len(a)):
        controlled_add(qc, problem_qubits[i], a[i], sum_reg, inverse=False)
    
    # Apply Z phase when sum == 27 (binary 11011)
    apply_phase_when_equal(qc, sum_reg, target)
    
    # Uncompute sum
    for i in range(len(a) - 1, -1, -1):
        controlled_add(qc, problem_qubits[i], a[i], sum_reg, inverse=True)


def controlled_add(qc: QuantumCircuit, control: int, value: int,
                   register: list[int], inverse: bool) -> None:
    """Add or subtract value from register, controlled by control qubit"""
    # Extract binary digits of value
    bits = [(value >> i) & 1 for i in range(len(register))]
    
    if inverse:
        # Reverse order for subtraction (uncompute)
        for i in range(len(register) - 1, -1, -1):
            if bits[i]:
                qc.cx(control, register[i])
    else:
        # Forward order for addition (compute)
        for i in range(len(register)):
            if bits[i]:
                qc.cx(control, register[i])


def apply_phase_when_equal(qc: QuantumCircuit, register: list[int],
                           target: int) -> None:
    """Apply Z phase when register equals target"""
    # Convert target to binary
    target_bits = bin(target)[2:].zfill(len(register))
    
    # Flip bits that should be 0 (so all bits are 1)
    for i in range(len(register)):
        if target_bits[len(register) - 1 - i] == '0':
            qc.x(register[i])
    
    # Apply multi-controlled phase: phase π when all controls are 1
    qc.mcp(np.pi, register[:-1], register[-1])
    
    # Flip bits back
    for i in range(len(register)):
        if target_bits[len(register) - 1 - i] == '0':
            qc.x(register[i])
