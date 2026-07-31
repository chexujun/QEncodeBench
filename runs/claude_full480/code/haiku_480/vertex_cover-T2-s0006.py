from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Grover oracle for vertex cover of size <= 3.
    
    Graph edges: (0,1), (0,4), (1,4), (2,3)
    f(x) = 1 iff x is a valid vertex cover of size <= 3
    
    Ancilla layout:
      0-3: temporary storage (edge coverage, then terms)
      4: all_covered flag
      5: at_least_4_bits flag  
      6: final_result (apply phase here)
    """
    
    a = ancilla_qubits
    p = problem_qubits
    
    def compute_or(q1, q2, target):
        """Compute target = target OR (q1 OR q2), assuming target initially 0."""
        qc.cx(q1, target)
        qc.cx(q2, target)
        qc.ccx(q1, q2, target)
    
    # ===== COMPUTE PHASE =====
    
    # Step 1: Compute edge coverage for each of 4 edges
    # Edge (0,1): a[0] = x[0] OR x[1]
    compute_or(p[0], p[1], a[0])
    # Edge (0,4): a[1] = x[0] OR x[4]
    compute_or(p[0], p[4], a[1])
    # Edge (1,4): a[2] = x[1] OR x[4]
    compute_or(p[1], p[4], a[2])
    # Edge (2,3): a[3] = x[2] OR x[3]
    compute_or(p[2], p[3], a[3])
    
    # Step 2: Compute all_covered = AND of all 4 edge coverages
    qc.mcx([a[0], a[1], a[2], a[3]], a[4])
    
    # Step 3: Compute at_least_4_bits (popcount >= 4) into a[5]
    # This is the OR of five 4-bit AND terms
    
    # Term 0: x[0] AND x[1] AND x[2] AND x[3]
    qc.mcx([p[0], p[1], p[2], p[3]], a[0])
    
    # Term 1: x[0] AND x[1] AND x[2] AND x[4]
    qc.mcx([p[0], p[1], p[2], p[4]], a[1])
    # OR term0 with term1: result into a[6]
    compute_or(a[0], a[1], a[6])
    
    # Term 2: x[0] AND x[1] AND x[3] AND x[4]
    qc.mcx([p[0], p[1], p[3], p[4]], a[0])
    # OR previous result with term2: result into a[1]
    compute_or(a[6], a[0], a[1])
    
    # Term 3: x[0] AND x[2] AND x[3] AND x[4]
    qc.mcx([p[0], p[2], p[3], p[4]], a[0])
    # OR previous result with term3: result into a[6]
    compute_or(a[1], a[0], a[6])
    
    # Term 4: x[1] AND x[2] AND x[3] AND x[4]
    qc.mcx([p[1], p[2], p[3], p[4]], a[0])
    # OR previous result with term4: final result into a[5]
    compute_or(a[6], a[0], a[5])
    
    # Step 4: Compute final_result = all_covered AND NOT(at_least_4_bits)
    qc.x(a[5])
    qc.ccx(a[4], a[5], a[6])
    qc.x(a[5])
    
    # Step 5: Apply phase
    qc.z(a[6])
    
    # ===== UNCOMPUTE PHASE =====
    
    # Reverse of step 4
    qc.x(a[5])
    qc.ccx(a[4], a[5], a[6])
    qc.x(a[5])
    
    # Reverse of step 3: uncompute OR and term operations in reverse order
    # Uncompute final OR(a[6], a[0], a[5])
    qc.ccx(a[6], a[0], a[5])
    qc.cx(a[0], a[5])
    qc.cx(a[6], a[5])
    
    # Uncompute term 4
    qc.mcx([p[1], p[2], p[3], p[4]], a[0])
    
    # Uncompute OR(a[1], a[0], a[6])
    qc.ccx(a[1], a[0], a[6])
    qc.cx(a[0], a[6])
    qc.cx(a[1], a[6])
    
    # Uncompute term 3
    qc.mcx([p[0], p[2], p[3], p[4]], a[0])
    
    # Uncompute OR(a[6], a[0], a[1])
    qc.ccx(a[6], a[0], a[1])
    qc.cx(a[0], a[1])
    qc.cx(a[6], a[1])
    
    # Uncompute term 2
    qc.mcx([p[0], p[1], p[3], p[4]], a[0])
    
    # Uncompute OR(a[1], a[0], a[6])
    qc.ccx(a[1], a[0], a[6])
    qc.cx(a[0], a[6])
    qc.cx(a[1], a[6])
    
    # Uncompute term 1
    qc.mcx([p[0], p[1], p[2], p[4]], a[1])
    
    # Uncompute OR(a[0], a[1], a[6])
    qc.ccx(a[0], a[1], a[6])
    qc.cx(a[1], a[6])
    qc.cx(a[0], a[6])
    
    # Uncompute term 0
    qc.mcx([p[0], p[1], p[2], p[3]], a[0])
    
    # Reverse of step 2
    qc.mcx([a[0], a[1], a[2], a[3]], a[4])
    
    # Reverse of step 1
    compute_or(p[2], p[3], a[3])
    compute_or(p[1], p[4], a[2])
    compute_or(p[0], p[4], a[1])
    compute_or(p[0], p[1], a[0])
