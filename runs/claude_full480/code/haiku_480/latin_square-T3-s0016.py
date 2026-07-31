from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    p0, p1, p2, p3, p4, p5, p6, p7 = problem_qubits
    a0, a1, a2, a3, a4, a5 = ancilla_qubits
    
    # COMPUTE PHASE: Mark valid Latin square completions
    
    # Condition 1: Cell 0 must decode to value 0 (code 00 or 11)
    # This means p0 == p1 (i.e., NOT(p0 XOR p1))
    qc.cx(p0, a0)
    qc.cx(p1, a0)  # a0 = p0 XOR p1
    qc.x(a0)       # a0 = NOT(p0 XOR p1) = (p0 == p1)
    
    # Condition 2: Cell 1 must decode to value 1 (code 01)
    # This means p2 == 1 AND p3 == 0 (i.e., p2 AND NOT(p3))
    qc.x(p3)  # flip p3
    qc.ccx(p2, p3, a1)  # a1 = p2 AND (flipped_p3) = p2 AND NOT(original_p3)
    qc.x(p3)  # flip p3 back
    
    # Condition 3: Cell 2 must decode to value 0 (code 00 or 11)
    # This means p4 == p5 (i.e., NOT(p4 XOR p5))
    qc.cx(p4, a2)
    qc.cx(p5, a2)  # a2 = p4 XOR p5
    qc.x(a2)       # a2 = NOT(p4 XOR p5) = (p4 == p5)
    
    # Condition 4: Cell 3 must decode to value 0 (code 00 or 11)
    # This means p6 == p7 (i.e., NOT(p6 XOR p7))
    qc.cx(p6, a3)
    qc.cx(p7, a3)  # a3 = p6 XOR p7
    qc.x(a3)       # a3 = NOT(p6 XOR p7) = (p6 == p7)
    
    # Combine all conditions with AND into a4
    qc.mcx([a0, a1, a2, a3], a4)  # a4 = a0 AND a1 AND a2 AND a3
    
    # APPLY PHASE
    qc.z(a4)
    
    # UNCOMPUTE PHASE
    qc.mcx([a0, a1, a2, a3], a4)  # uncompute a4
    
    # Uncompute Condition 4
    qc.x(a3)
    qc.cx(p7, a3)
    qc.cx(p6, a3)
    
    # Uncompute Condition 3
    qc.x(a2)
    qc.cx(p5, a2)
    qc.cx(p4, a2)
    
    # Uncompute Condition 2
    qc.x(p3)
    qc.ccx(p2, p3, a1)
    qc.x(p3)
    
    # Uncompute Condition 1
    qc.x(a0)
    qc.cx(p1, a0)
    qc.cx(p0, a0)
