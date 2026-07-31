from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]
    a0, a1, a2, a3, a4, a5 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3], ancilla_qubits[4], ancilla_qubits[5]
    
    # Compute clause false indicators (1 = clause is false)
    # Clause 1: (¬x1 ∨ ¬x2 ∨ ¬x3) is false iff (x1 AND x2 AND x3)
    qc.mcx([x1, x2, x3], a0)
    
    # Clause 2: (x0 ∨ ¬x2 ∨ ¬x3) is false iff (¬x0 AND x2 AND x3)
    qc.cx(x0, a5)
    qc.x(a5)
    qc.mcx([a5, x2, x3], a1)
    qc.x(a5)
    qc.cx(x0, a5)
    
    # Clause 3: (x1 ∨ ¬x2 ∨ x3) is false iff (¬x1 AND x2 AND ¬x3)
    qc.cx(x1, a5)
    qc.x(a5)
    qc.cx(x3, a2)
    qc.x(a2)
    qc.mcx([a5, x2, a2], a3)
    qc.x(a2)
    qc.cx(x3, a2)
    qc.x(a5)
    qc.cx(x1, a5)
    
    # Clause 4: (¬x1 ∨ x2 ∨ x3) is false iff (x1 AND ¬x2 AND ¬x3)
    qc.cx(x2, a5)
    qc.x(a5)
    qc.cx(x3, a2)
    qc.x(a2)
    qc.mcx([x1, a5, a2], a4)
    qc.x(a2)
    qc.cx(x3, a2)
    qc.x(a5)
    qc.cx(x2, a5)
    
    # Clause 5: (x1 ∨ ¬x2 ∨ ¬x3) is false iff (¬x1 AND x2 AND x3)
    qc.cx(x1, a5)
    qc.x(a5)
    qc.mcx([a5, x2, x3], a2)
    qc.x(a5)
    qc.cx(x1, a5)
    
    # Compute AND(NOT a0, NOT a1, NOT a2, NOT a3, NOT a4) into a5
    # This equals 1 iff all clauses are satisfied
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.x(a3)
    qc.x(a4)
    qc.mcx([a0, a1, a2, a3, a4], a5)
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.x(a3)
    qc.x(a4)
    
    # Apply phase -1 when a5 = 1 (all clauses satisfied)
    qc.z(a5)
    
    # Uncompute in reverse order
    # Uncompute AND result
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.x(a3)
    qc.x(a4)
    qc.mcx([a0, a1, a2, a3, a4], a5)
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.x(a3)
    qc.x(a4)
    
    # Uncompute clause 5
    qc.cx(x1, a5)
    qc.x(a5)
    qc.mcx([a5, x2, x3], a2)
    qc.x(a5)
    qc.cx(x1, a5)
    
    # Uncompute clause 4
    qc.cx(x2, a5)
    qc.x(a5)
    qc.cx(x3, a2)
    qc.x(a2)
    qc.mcx([x1, a5, a2], a4)
    qc.x(a2)
    qc.cx(x3, a2)
    qc.x(a5)
    qc.cx(x2, a5)
    
    # Uncompute clause 3
    qc.cx(x1, a5)
    qc.x(a5)
    qc.cx(x3, a2)
    qc.x(a2)
    qc.mcx([a5, x2, a2], a3)
    qc.x(a2)
    qc.cx(x3, a2)
    qc.x(a5)
    qc.cx(x1, a5)
    
    # Uncompute clause 2
    qc.cx(x0, a5)
    qc.x(a5)
    qc.mcx([a5, x2, x3], a1)
    qc.x(a5)
    qc.cx(x0, a5)
    
    # Uncompute clause 1
    qc.mcx([x1, x2, x3], a0)
