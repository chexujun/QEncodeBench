from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], 
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    a = ancilla_qubits
    
    def compute_and_3(q1, q2, q3, out, temp, flip1=False, flip2=False, flip3=False):
        """Compute (literal_1 AND literal_2 AND literal_3) into out using temp.
        Flips indicate which qubits to negate."""
        if flip1:
            qc.x(q1)
        if flip2:
            qc.x(q2)
        if flip3:
            qc.x(q3)
        
        qc.ccx(q1, q2, temp)
        qc.ccx(temp, q3, out)
        qc.ccx(q1, q2, temp)
        
        if flip3:
            qc.x(q3)
        if flip2:
            qc.x(q2)
        if flip1:
            qc.x(q1)
    
    # Compute each clause as NOT(AND of violation condition)
    # Clause 0: (x0 OR NOT x1 OR NOT x4) = NOT(NOT x0 AND x1 AND x4)
    compute_and_3(x[0], x[1], x[4], a[0], a[6], flip1=True)
    qc.x(a[0])
    
    # Clause 1: (NOT x0 OR NOT x1 OR x4) = NOT(x0 AND x1 AND NOT x4)
    compute_and_3(x[0], x[1], x[4], a[1], a[6], flip3=True)
    qc.x(a[1])
    
    # Clause 2: (NOT x0 OR x2 OR NOT x3) = NOT(x0 AND NOT x2 AND x3)
    compute_and_3(x[0], x[2], x[3], a[2], a[6], flip2=True)
    qc.x(a[2])
    
    # Clause 3: (NOT x0 OR NOT x3 OR x4) = NOT(x0 AND x3 AND NOT x4)
    compute_and_3(x[0], x[3], x[4], a[3], a[6], flip3=True)
    qc.x(a[3])
    
    # Clause 4: (NOT x2 OR x3 OR x4) = NOT(x2 AND NOT x3 AND NOT x4)
    compute_and_3(x[2], x[3], x[4], a[4], a[6], flip2=True, flip3=True)
    qc.x(a[4])
    
    # Clause 5: (NOT x1 OR x3 OR x4) = NOT(x1 AND NOT x3 AND NOT x4)
    compute_and_3(x[1], x[3], x[4], a[5], a[6], flip2=True, flip3=True)
    qc.x(a[5])
    
    # Apply phase when all clauses are satisfied
    qc.mcx([a[0], a[1], a[2], a[3], a[4], a[5]], a[6])
    qc.z(a[6])
    qc.mcx([a[0], a[1], a[2], a[3], a[4], a[5]], a[6])
    
    # Uncompute clauses in reverse order
    qc.x(a[5])
    compute_and_3(x[1], x[3], x[4], a[5], a[6], flip2=True, flip3=True)
    
    qc.x(a[4])
    compute_and_3(x[2], x[3], x[4], a[4], a[6], flip2=True, flip3=True)
    
    qc.x(a[3])
    compute_and_3(x[0], x[3], x[4], a[3], a[6], flip3=True)
    
    qc.x(a[2])
    compute_and_3(x[0], x[2], x[3], a[2], a[6], flip2=True)
    
    qc.x(a[1])
    compute_and_3(x[0], x[1], x[4], a[1], a[6], flip3=True)
    
    qc.x(a[0])
    compute_and_3(x[0], x[1], x[4], a[0], a[6], flip1=True)
