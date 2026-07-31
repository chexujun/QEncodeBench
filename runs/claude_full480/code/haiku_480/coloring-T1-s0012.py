from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Phase oracle for 3-coloring of a 5-vertex graph.
    Applies phase -1 to valid colorings.
    """
    edges = [(0, 3), (1, 3), (2, 4), (3, 4)]
    
    # Extract qubits for each vertex color code
    def get_vertex_qubits(v):
        return problem_qubits[2*v], problem_qubits[2*v + 1]
    
    # Compute monochromatic status for each edge into ancilla[0:4]
    for i, (u, v) in enumerate(edges):
        u_b0, u_b1 = get_vertex_qubits(u)
        v_b0, v_b1 = get_vertex_qubits(v)
        result = ancilla_qubits[i]
        
        # Compute: same_color = ((b1_u XNOR b1_v) AND (b0_u XNOR b0_v)) 
        #                    OR ((b1_u XNOR b0_u) AND (b1_v XNOR b0_v))
        # Using temporary ancillas for intermediate values
        temp1 = ancilla_qubits[5 + 2*i]      # (b1_u XNOR b1_v)
        temp2 = ancilla_qubits[5 + 2*i + 1]  # (b0_u XNOR b0_v)
        
        # Compute XNOR for b1 bits: result is 1 if equal
        qc.cx(u_b1, temp1)
        qc.cx(v_b1, temp1)
        qc.x(temp1)
        
        # Compute XNOR for b0 bits
        qc.cx(u_b0, temp2)
        qc.cx(v_b0, temp2)
        qc.x(temp2)
        
        # AND temp1 and temp2 into result (using Toffoli)
        qc.ccx(temp1, temp2, result)
        
        # Uncompute temp1 and temp2
        qc.x(temp2)
        qc.cx(v_b0, temp2)
        qc.cx(u_b0, temp2)
        
        qc.x(temp1)
        qc.cx(v_b1, temp1)
        qc.cx(u_b1, temp1)
    
    # Compute OR of all edge monochromatic flags
    # OR can be built as NOT(AND of complements)
    violation = ancilla_qubits[4]
    or_temp = ancilla_qubits[13]  # temporary for OR computation
    
    # Use the structure: A OR B OR C OR D = NOT(NOT(A) AND NOT(B) AND NOT(C) AND NOT(D))
    # First, compute AND of complements
    or_temp_val = ancilla_qubits[14]  # another temporary
    
    for i in range(4):
        qc.x(ancilla_qubits[i])  # Flip all mono flags
    
    # Compute AND chain: use Toffoli-based AND
    temp_and = ancilla_qubits[14]
    qc.ccx(ancilla_qubits[0], ancilla_qubits[1], temp_and)
    qc.ccx(temp_and, ancilla_qubits[2], or_temp)
    qc.ccx(or_temp, ancilla_qubits[3], violation)
    
    # Uncompute AND chain
    qc.ccx(or_temp, ancilla_qubits[3], violation)
    qc.ccx(temp_and, ancilla_qubits[2], or_temp)
    qc.ccx(ancilla_qubits[0], ancilla_qubits[1], temp_and)
    
    for i in range(4):
        qc.x(ancilla_qubits[i])  # Flip back
    
    # violation qubit now holds: NOT(all complements) = (at least one mono)
    # We want to apply Z when no edges are monochromatic, i.e., when violation=0
    
    # Apply X-Z-X pattern to flip the control condition
    qc.x(violation)
    qc.z(violation)
    qc.x(violation)
    
    # Uncompute violation flag (mirror of compute)
    for i in range(4):
        qc.x(ancilla_qubits[i])
    
    temp_and = ancilla_qubits[14]
    qc.ccx(ancilla_qubits[0], ancilla_qubits[1], temp_and)
    qc.ccx(temp_and, ancilla_qubits[2], or_temp)
    qc.ccx(or_temp, ancilla_qubits[3], violation)
    
    qc.ccx(or_temp, ancilla_qubits[3], violation)
    qc.ccx(temp_and, ancilla_qubits[2], or_temp)
    qc.ccx(ancilla_qubits[0], ancilla_qubits[1], temp_and)
    
    for i in range(4):
        qc.x(ancilla_qubits[i])
    
    # Uncompute edge monochromatic flags (in reverse)
    for i in range(3, -1, -1):
        u, v = edges[i]
        u_b0, u_b1 = get_vertex_qubits(u)
        v_b0, v_b1 = get_vertex_qubits(v)
        result = ancilla_qubits[i]
        
        temp1 = ancilla_qubits[5 + 2*i]
        temp2 = ancilla_qubits[5 + 2*i + 1]
        
        qc.ccx(temp1, temp2, result)
        
        qc.x(temp2)
        qc.cx(v_b0, temp2)
        qc.cx(u_b0, temp2)
        
        qc.x(temp1)
        qc.cx(v_b1, temp1)
        qc.cx(u_b1, temp1)
