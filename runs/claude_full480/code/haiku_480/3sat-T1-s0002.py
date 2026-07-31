from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2 = problem_qubits
    a0, a1, a2, a3, a4 = ancilla_qubits
    
    # Compute unsatisfied condition for each clause into ancillas a0, a1, a2, a3
    
    # Clause 1: (NOT x0 OR x1 OR NOT x2) unsatisfied when x0=1, x1=0, x2=1
    qc.x(x1)
    qc.ccx(x0, x2, a0)
    qc.ccx(a0, x1, a0)
    qc.x(x1)
    
    # Clause 2: (NOT x0 OR NOT x1 OR x2) unsatisfied when x0=1, x1=1, x2=0
    qc.x(x2)
    qc.ccx(x0, x1, a1)
    qc.ccx(a1, x2, a1)
    qc.x(x2)
    
    # Clause 3: (x0 OR x1 OR x2) unsatisfied when x0=0, x1=0, x2=0
    qc.x(x0)
    qc.x(x1)
    qc.x(x2)
    qc.ccx(x0, x1, a2)
    qc.ccx(a2, x2, a2)
    qc.x(x2)
    qc.x(x1)
    qc.x(x0)
    
    # Clause 4: (NOT x0 OR x1 OR x2) unsatisfied when x0=1, x1=0, x2=0
    qc.x(x1)
    qc.x(x2)
    qc.ccx(x0, x2, a3)
    qc.ccx(a3, x1, a3)
    qc.x(x1)
    qc.x(x2)
    
    # Compute AND of (NOT a0) AND (NOT a1) AND (NOT a2) AND (NOT a3) into a4
    qc.x(a0)
    qc.x(a1)
    qc.x(a3)
    qc.ccx(a0, a1, a4)
    qc.ccx(a4, a2, a4)
    qc.ccx(a4, a3, a4)
    qc.x(a3)
    qc.x(a1)
    qc.x(a0)
    
    # Apply phase -1 if all clauses satisfied
    qc.z(a4)
    
    # Uncompute AND
    qc.x(a0)
    qc.x(a1)
    qc.x(a3)
    qc.ccx(a4, a3, a4)
    qc.ccx(a4, a2, a4)
    qc.ccx(a0, a1, a4)
    qc.x(a3)
    qc.x(a1)
    qc.x(a0)
    
    # Uncompute clauses in reverse order
    
    # Uncompute Clause 4
    qc.x(x1)
    qc.x(x2)
    qc.ccx(a3, x1, a3)
    qc.ccx(x0, x2, a3)
    qc.x(x2)
    qc.x(x1)
    
    # Uncompute Clause 3
    qc.x(x0)
    qc.x(x1)
    qc.x(x2)
    qc.ccx(a2, x2, a2)
    qc.ccx(x0, x1, a2)
    qc.x(x2)
    qc.x(x1)
    qc.x(x0)
    
    # Uncompute Clause 2
    qc.x(x2)
    qc.ccx(a1, x2, a1)
    qc.ccx(x0, x1, a1)
    qc.x(x2)
    
    # Uncompute Clause 1
    qc.x(x1)
    qc.ccx(a0, x1, a0)
    qc.ccx(x0, x2, a0)
    qc.x(x1)
