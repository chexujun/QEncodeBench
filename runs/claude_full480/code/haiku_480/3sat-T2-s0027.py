import numpy as np
from qiskit import QuantumCircuit

def build_oracle(qc, problem_qubits, ancilla_qubits):
    p = problem_qubits
    a = ancilla_qubits
    
    def compute_clause(qc, c1, c1_flip, c2, c2_flip, c3, c3_flip, output):
        """Compute NOT(c1_val AND c2_val AND c3_val) into output, using a[6] as temporary."""
        if c1_flip:
            qc.x(c1)
        if c2_flip:
            qc.x(c2)
        if c3_flip:
            qc.x(c3)
        
        qc.ccx(c1, c2, a[6])
        qc.ccx(a[6], c3, output)
        qc.x(output)
        qc.ccx(c1, c2, a[6])
        
        if c3_flip:
            qc.x(c3)
        if c2_flip:
            qc.x(c2)
        if c1_flip:
            qc.x(c1)
    
    def uncompute_clause(qc, c1, c1_flip, c2, c2_flip, c3, c3_flip, output):
        """Uncompute the clause (mirror of compute)."""
        if c1_flip:
            qc.x(c1)
        if c2_flip:
            qc.x(c2)
        if c3_flip:
            qc.x(c3)
        
        qc.ccx(c1, c2, a[6])
        qc.x(output)
        qc.ccx(a[6], c3, output)
        qc.ccx(c1, c2, a[6])
        
        if c3_flip:
            qc.x(c3)
        if c2_flip:
            qc.x(c2)
        if c1_flip:
            qc.x(c1)
    
    # Compute each clause
    compute_clause(qc, p[3], False, p[4], False, p[5], False, a[0])
    compute_clause(qc, p[1], True, p[2], False, p[4], True, a[1])
    compute_clause(qc, p[1], False, p[3], False, p[4], True, a[2])
    compute_clause(qc, p[1], True, p[3], False, p[4], False, a[3])
    compute_clause(qc, p[1], False, p[3], True, p[4], False, a[4])
    compute_clause(qc, p[0], False, p[3], True, p[5], False, a[5])
    
    # Apply phase gate
    qc.x(a[6])
    qc.mcp(np.pi, [a[0], a[1], a[2], a[3], a[4], a[5]], a[6])
    qc.x(a[6])
    
    # Uncompute clauses (in reverse order)
    uncompute_clause(qc, p[0], False, p[3], True, p[5], False, a[5])
    uncompute_clause(qc, p[1], False, p[3], True, p[4], False, a[4])
    uncompute_clause(qc, p[1], True, p[3], False, p[4], False, a[3])
    uncompute_clause(qc, p[1], False, p[3], False, p[4], True, a[2])
    uncompute_clause(qc, p[1], True, p[2], False, p[4], True, a[1])
    uncompute_clause(qc, p[3], False, p[4], False, p[5], False, a[0])
