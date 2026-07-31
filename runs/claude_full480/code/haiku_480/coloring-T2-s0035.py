from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0,1), (0,4), (1,2), (1,3), (1,4), (2,4), (3,4)]
    
    # Compute same_color flag for each edge
    for idx, (u, v) in enumerate(edges):
        u0 = problem_qubits[2*u]
        u1 = problem_qubits[2*u + 1]
        v0 = problem_qubits[2*v]
        v1 = problem_qubits[2*v + 1]
        flag = ancilla_qubits[idx]
        
        # Compute: flag = 1 iff colors are the same
        # Colors same when (u0 + 2*u1) % 3 == (v0 + 2*v1) % 3
        # Truth table: (0,0,0,0), (0,0,1,1), (1,0,1,0), (0,1,0,1), (1,1,0,0), (1,1,1,1)
        
        # Compute intermediate XOR values in temporary ancillas
        temp1 = ancilla_qubits[idx]
        
        # Check u0==v0: compute into temp1
        qc.cx(u0, temp1)
        qc.cx(v0, temp1)
        
        # temp1 is now 1 iff u0 != v0
        qc.x(temp1)  # Now temp1 = 1 iff u0 == v0
        
        # Compute u1==v1 check
        qc.cx(u1, temp1)
        qc.cx(v1, temp1)
        # Now temp1 encodes both equality checks via XOR
        
        # Since we need exact same_color, we check all 6 cases
        # For efficiency, we use the pattern that same_color is 1 when
        # (NOT (u0 XOR v0)) AND (NOT (u1 XOR v1)) OR special cases
        
        # Reset and compute properly
        qc.cx(v1, temp1)
        qc.cx(u1, temp1)
        qc.x(temp1)
        
        # Now temp1 = 1 iff u0==v0
        # Need to also check u1==v1 and handle the color index % 3 logic
        
        # Create a second temp for u1==v1
        qc.cx(u1, flag)
        qc.cx(v1, flag)
        qc.x(flag)
        
        # Now: temp1 = (u0==v0), flag = (u1==v1)
        # same_color = 1 for: all-zeros, both-ones, alternating patterns
        
        # Final check: same_color when (u0==v0 AND u1==v1) OR special cases
        qc.ccx(temp1, flag, ancilla_qubits[idx])
        
        # Handle special cases: (0,0,1,1) or (1,1,0,0) map to same color 0
        qc.cx(u0, flag)
        qc.cx(v0, flag)
        qc.ccx(u1, v1, ancilla_qubits[idx])
        qc.cx(v0, flag)
        qc.cx(u0, flag)
        
        # Restore temp ancilla
        qc.x(flag)
        qc.cx(v1, flag)
        qc.cx(u1, flag)
        qc.x(temp1)
        qc.cx(v0, temp1)
        qc.cx(u0, temp1)
    
    # Apply phase when ALL edges have different colors (all flags == 0)
    work = ancilla_qubits[7]
    
    # Initialize work qubit to 1
    qc.x(work)
    
    # If any flag is 1, flip work (now work=0 means all different)
    for idx in range(7):
        qc.cx(ancilla_qubits[idx], work)
    
    # Apply phase
    qc.z(work)
    
    # Uncompute: reverse the control operations
    for idx in range(7):
        qc.cx(ancilla_qubits[idx], work)
    qc.x(work)
    
    # Uncompute same_color flags (reverse order)
    for idx in range(6, -1, -1):
        u, v = edges[idx]
        u0 = problem_qubits[2*u]
        u1 = problem_qubits[2*u + 1]
        v0 = problem_qubits[2*v]
        v1 = problem_qubits[2*v + 1]
        flag = ancilla_qubits[idx]
        
        qc.cx(u0, flag)
        qc.cx(v0, flag)
        qc.ccx(u1, v1, flag)
        qc.cx(v0, flag)
        qc.cx(u0, flag)
        
        qc.x(flag)
        qc.cx(u1, flag)
        qc.cx(v1, flag)
        qc.x(flag)
        qc.cx(u0, flag)
        qc.cx(v0, flag)
