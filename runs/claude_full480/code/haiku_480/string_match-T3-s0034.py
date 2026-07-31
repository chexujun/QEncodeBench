from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Grover phase oracle for pattern matching.
    Pattern: "0100" (length 4)
    f(x) = 1 iff the pattern appears at some contiguous offset in the 8-bit string x
    
    Pattern semantics: position i in pattern matches s_(o+i) where '0' means must be 0,
    '1' means must be 1, and '?' matches any bit (not present in this instance).
    
    Uses compute-phase-uncompute discipline:
    1. Compute match predicates for each of 5 possible offsets
    2. Compute their OR using De Morgan: OR = NOT(AND of NOTs)
    3. Apply Z phase gate
    4. Uncompute everything in reverse order
    """
    s = problem_qubits
    
    # Allocate ancillas: 5 for match predicates (one per offset), 1 for OR result
    match_temps = ancilla_qubits[0:5]
    or_result = ancilla_qubits[5]
    
    # ==================== COMPUTE PHASE ====================
    
    # For each offset [0,4], compute: NOT s[offset] AND s[offset+1] AND NOT s[offset+2] AND NOT s[offset+3]
    for i, offset in enumerate(range(5)):
        match_anc = match_temps[i]
        
        # Flip bits that must be 0 in the pattern
        qc.x(s[offset])
        qc.x(s[offset + 2])
        qc.x(s[offset + 3])
        
        # Compute AND of all four bits (all must be 1 for match)
        qc.mcx([s[offset], s[offset+1], s[offset+2], s[offset+3]], match_anc)
        
        # Restore problem qubits
        qc.x(s[offset])
        qc.x(s[offset + 2])
        qc.x(s[offset + 3])
    
    # Compute OR of all matches using De Morgan's law: OR(a,b,c,d,e) = NOT(AND(NOT a, NOT b, NOT c, NOT d, NOT e))
    
    # X all match_temps to get their negations
    for anc in match_temps:
        qc.x(anc)
    
    # Compute AND of the negated matches
    qc.mcx(match_temps, or_result)
    
    # Apply X to negate the AND result (gives us the OR via De Morgan)
    qc.x(or_result)
    
    # Restore match_temps by flipping back
    for anc in match_temps:
        qc.x(anc)
    
    # ==================== PHASE GATE ====================
    # or_result now contains f(x) = 1 iff pattern matches at some offset
    # Apply -1 phase if f(x) = 1
    qc.z(or_result)
    
    # ==================== UNCOMPUTE PHASE ====================
    # Reverse all operations in reverse order to restore ancillas to |0⟩
    
    # Uncompute the OR computation by mirroring the compute phase steps
    # X all match_temps
    for anc in match_temps:
        qc.x(anc)
    
    # Negate or_result
    qc.x(or_result)
    
    # Uncompute AND (mcx is self-inverse)
    qc.mcx(match_temps, or_result)
    
    # X all match_temps to restore
    for anc in match_temps:
        qc.x(anc)
    
    # Uncompute match predicates for each offset (in reverse order)
    for i in range(4, -1, -1):
        offset = i
        match_anc = match_temps[i]
        
        # Mirror the match computation
        qc.x(s[offset])
        qc.x(s[offset + 2])
        qc.x(s[offset + 3])
        
        qc.mcx([s[offset], s[offset+1], s[offset+2], s[offset+3]], match_anc)
        
        qc.x(s[offset])
        qc.x(s[offset + 2])
        qc.x(s[offset + 3])
