from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [13, 4, 4, 2, 6]
    target = 27
    target_bits = [(target >> i) & 1 for i in range(5)]
    
    sum_qubits = ancilla_qubits[0:5]
    
    # COMPUTE: Add each selected element to the sum
    for i, val in enumerate(a):
        for _ in range(val):
            add_1_if_selected(qc, problem_qubits[i], sum_qubits)
    
    # PHASE: Apply phase -1 if sum equals target
    apply_phase_if_equal(qc, sum_qubits, target_bits)
    
    # UNCOMPUTE: Subtract each selected element from the sum
    for i, val in enumerate(a):
        for _ in range(val):
            add_1_if_selected(qc, problem_qubits[i], sum_qubits)


def add_1_if_selected(qc: QuantumCircuit, control: int, reg: list[int]) -> None:
    """Conditionally add 1 to binary number in reg if control qubit is 1."""
    n = len(reg)
    # Carry propagation from MSB down to LSB using Toffoli gates
    for i in range(n - 2, -1, -1):
        qc.ccx(control, reg[i], reg[i + 1])
    # Flip least significant bit
    qc.cx(control, reg[0])


def apply_phase_if_equal(qc: QuantumCircuit, reg: list[int], target_bits: list[int]) -> None:
    """Apply phase -1 to state if reg matches target."""
    # Flip bits that should be 0 for the match check
    for i, bit in enumerate(target_bits):
        if bit == 0:
            qc.x(reg[i])
    
    # Apply multi-controlled phase gate (Z gate when all controls are 1)
    qc.mcp(np.pi, reg[:-1], reg[-1])
    
    # Flip bits back to restore original state
    for i, bit in enumerate(target_bits):
        if bit == 0:
            qc.x(reg[i])
