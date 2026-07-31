from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q0, q1, q2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    a0, a1, a2, a3, a4 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3], ancilla_qubits[4]
    
    # Clause 1: (NOT x0 OR x1 OR x2) = NOT(x0 AND NOT x1 AND NOT x2)
    qc.x(q1)
    qc.x(q2)
    qc.mcx([q0, q1, q2], a0)
    qc.x(q2)
    qc.x(q1)
    qc.x(a0)
    
    # Clause 2: (NOT x0 OR x1 OR NOT x2) = NOT(x0 AND NOT x1 AND x2)
    qc.x(q1)
    qc.mcx([q0, q1, q2], a1)
    qc.x(q1)
    qc.x(a1)
    
    # Clause 3: (x0 OR NOT x1 OR NOT x2) = NOT(NOT x0 AND x1 AND x2)
    qc.x(q0)
    qc.mcx([q0, q1, q2], a2)
    qc.x(q0)
    qc.x(a2)
    
    # Clause 4: (NOT x0 OR NOT x1 OR NOT x2) = NOT(x0 AND x1 AND x2)
    qc.mcx([q0, q1, q2], a3)
    qc.x(a3)
    
    # Compute AND of all clauses
    qc.mcx([a0, a1, a2, a3], a4)
    
    # Apply phase
    qc.z(a4)
    
    # Uncompute AND
    qc.mcx([a0, a1, a2, a3], a4)
    
    # Uncompute Clause 4
    qc.x(a3)
    qc.mcx([q0, q1, q2], a3)
    
    # Uncompute Clause 3
    qc.x(a2)
    qc.x(q0)
    qc.mcx([q0, q1, q2], a2)
    qc.x(q0)
    
    # Uncompute Clause 2
    qc.x(a1)
    qc.x(q1)
    qc.mcx([q0, q1, q2], a1)
    qc.x(q1)
    
    # Uncompute Clause 1
    qc.x(a0)
    qc.x(q1)
    qc.x(q2)
    qc.mcx([q0, q1, q2], a0)
    qc.x(q2)
    qc.x(q1)
