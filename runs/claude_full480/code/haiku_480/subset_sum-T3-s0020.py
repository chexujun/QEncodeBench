from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [14, 4, 12, 8, 7]
    target = 12
    s = ancilla_qubits[:6]
    
    # Forward pass: add each element to accumulator (ripple-carry adder)
    for i in range(5):
        add_constant_controlled(qc, problem_qubits[i], a[i], s)
    
    # Phase: apply Z gate if sum equals target (12 = binary 001100)
    apply_phase_if_equal(qc, s, target)
    
    # Backward pass: subtract each element (uncompute in reverse order)
    for i in range(4, -1, -1):
        add_constant_controlled(qc, problem_qubits[i], a[i], s)


def add_constant_controlled(qc, control, constant, reg):
    """Add constant to register when control qubit is 1, using ripple-carry."""
    n = len(reg)
    bits = [(constant >> i) & 1 for i in range(n)]
    
    for i in range(n - 1):
        if bits[i] == 0:
            continue
        # Propagate carries from position i onwards
        for j in range(i, n - 1):
            qc.ccx(control, reg[j], reg[j + 1])
        # XOR the current bit
        qc.cx(control, reg[i])
    
    # Handle MSB
    if bits[n - 1] == 1:
        qc.cx(control, reg[n - 1])


def apply_phase_if_equal(qc, reg, target):
    """Apply Z phase when reg equals target (12 = 001100 binary)."""
    # Convert target to binary: 12 = [0,0,1,1,0,0]
    target_bits = [(target >> i) & 1 for i in range(len(reg))]
    
    # Flip bits where target is 0 (positions 0,1,4,5)
    for i in range(len(reg)):
        if target_bits[i] == 0:
            qc.x(reg[i])
    
    # Now apply multi-controlled phase: all qubits are 1 iff sum == target
    qc.mcp(np.pi, reg[:-1], reg[-1])
    
    # Flip bits back
    for i in range(len(reg)):
        if target_bits[i] == 0:
            qc.x(reg[i])
