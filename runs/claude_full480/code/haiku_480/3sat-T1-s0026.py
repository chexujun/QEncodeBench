from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q0, q1, q2 = problem_qubits
    a0, a1, a2, a3, a4 = ancilla_qubits
    
    # Compute clause 1: (x0 OR x1 OR NOT x2)
    # False iff x0=0, x1=0, x2=1
    qc.x(a0)
    qc.mcx([q0, q1, q2], a0, ctrl_state="001")
    
    # Compute clause 2: (x0 OR x1 OR x2)
    # False iff x0=0, x1=0, x2=0
    qc.x(a1)
    qc.mcx([q0, q1, q2], a1, ctrl_state="000")
    
    # Compute clause 3: (NOT x0 OR NOT x1 OR x2)
    # False iff x0=1, x1=1, x2=0
    qc.x(a2)
    qc.mcx([q0, q1, q2], a2, ctrl_state="110")
    
    # Compute clause 4: (x0 OR NOT x1 OR NOT x2)
    # False iff x0=0, x1=1, x2=1
    qc.x(a3)
    qc.mcx([q0, q1, q2], a3, ctrl_state="011")
    
    # AND all clauses: a4 = a0 AND a1 AND a2 AND a3
    qc.mcx([a0, a1, a2, a3], a4)
    
    # Apply phase
    qc.z(a4)
    
    # Uncompute: AND
    qc.mcx([a0, a1, a2, a3], a4)
    
    # Uncompute: clauses (in reverse order)
    qc.mcx([q0, q1, q2], a3, ctrl_state="011")
    qc.x(a3)
    
    qc.mcx([q0, q1, q2], a2, ctrl_state="110")
    qc.x(a2)
    
    qc.mcx([q0, q1, q2], a1, ctrl_state="000")
    qc.x(a1)
    
    qc.mcx([q0, q1, q2], a0, ctrl_state="001")
    qc.x(a0)
