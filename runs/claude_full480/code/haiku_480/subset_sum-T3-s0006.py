from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [3, 4, 5, 14, 13]
    target = 21
    
    # COMPUTE: Add each element if selected
    for i, value in enumerate(a):
        controlled_add(qc, problem_qubits[i], value, ancilla_qubits)
    
    # PHASE: Apply -1 if sum equals target
    apply_conditional_phase(qc, ancilla_qubits, target)
    
    # UNCOMPUTE: Subtract each element (XOR is self-inverse)
    for i in range(len(a) - 1, -1, -1):
        controlled_add(qc, problem_qubits[i], a[i], ancilla_qubits)

def controlled_add(qc, control, value, ancillas):
    """XOR value into ancillas (controlled by control qubit)"""
    n = len(ancillas)
    value_bits = format(value, f'0{n}b')[::-1]  # LSB first
    
    for i, bit in enumerate(value_bits):
        if bit == '1':
            qc.cx(control, ancillas[i])

def apply_conditional_phase(qc, ancillas, target):
    """Apply Z phase if ancillas represent target value"""
    n = len(ancillas)
    target_bits = format(target, f'0{n}b')[::-1]  # LSB first
    
    # Flip bits that should be 0
    for i, bit in enumerate(target_bits):
        if bit == '0':
            qc.x(ancillas[i])
    
    # Apply multi-controlled Z
    apply_multi_controlled_z(qc, ancillas)
    
    # Unflip bits
    for i, bit in enumerate(target_bits):
        if bit == '0':
            qc.x(ancillas[i])

def apply_multi_controlled_z(qc, qubits):
    """Apply Z controlled by all qubits being |1>"""
    if len(qubits) == 0:
        return
    elif len(qubits) == 1:
        qc.z(qubits[0])
    elif len(qubits) == 2:
        qc.cz(qubits[0], qubits[1])
    elif len(qubits) == 3:
        qc.h(qubits[2])
        qc.ccx(qubits[0], qubits[1], qubits[2])
        qc.h(qubits[2])
    else:
        # For 4+ qubits: H + multi-controlled X + H
        target = qubits[-1]
        controls = qubits[:-1]
        qc.h(target)
        qc.mcx(controls, target)
        qc.h(target)
