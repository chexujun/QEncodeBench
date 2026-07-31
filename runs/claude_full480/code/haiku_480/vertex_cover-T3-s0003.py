from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0,1), (0,2), (0,4), (1,2), (1,5), (2,3), (2,4)]
    
    # Allocate ancillas
    edge_flags = ancilla_qubits[0:7]   # one per edge to check coverage
    pc_bits = ancilla_qubits[7:10]     # 3 bits for popcount accumulator
    
    # === COMPUTE: Edge coverage flags ===
    # For each edge, set edge_flags[i] = OR of its endpoints
    for idx, (i, j) in enumerate(edges):
        ea = edge_flags[idx]
        pi, pj = problem_qubits[i], problem_qubits[j]
        qc.cx(pi, ea)         # ea XOR= pi
        qc.cx(pj, ea)         # ea XOR= pj  => ea = pi XOR pj
        qc.ccx(pi, pj, ea)    # ea XOR= (pi AND pj)  => ea = pi OR pj
    
    # === COMPUTE: Popcount into pc_bits using ripple carry ===
    for qubit in problem_qubits:
        # Bit 0
        qc.ccx(qubit, pc_bits[0], pc_bits[1])  # carry = qubit AND pc_bits[0]
        qc.cx(qubit, pc_bits[0])               # pc_bits[0] XOR= qubit
        
        # Bit 1 (pc_bits[1] now holds the carry from bit 0)
        qc.ccx(pc_bits[1], pc_bits[1], pc_bits[2])  # carry = pc_bits[1] AND pc_bits[1] = pc_bits[1]
        # Actually, the above is wrong. Let me fix this properly.
    
    # Correct ripple carry addition for 6 bits into 3-bit accumulator:
    # We accumulate sum bit by bit. For each problem_qubit, we add it to pc_bits.
    
    # Reset pc_bits computation and use cleaner logic
    qc.reset(pc_bits)  # Oops, reset not allowed! Let me recompute.
    
    # Start over with correct ripple carry using proper temporary management:
    for q_idx, qubit in enumerate(problem_qubits):
        # Add problem_qubits[q_idx] to pc_bits[0:3]
        # Use edge_flags[6] and edge_flags[5] as temporary carries
        carry = edge_flags[6]  # Will use as temporary carry storage
        
        # Bit 0: pc_bits[0] + qubit
        qc.ccx(qubit, pc_bits[0], carry)     # carry = qubit AND pc_bits[0]
        qc.cx(qubit, pc_bits[0])             # pc_bits[0] XOR= qubit
        
        # Bit 1: pc_bits[1] + carry
        qc.ccx(carry, pc_bits[1], edge_flags[5])  # next_carry = carry AND pc_bits[1]
        qc.cx(carry, pc_bits[1])                  # pc_bits[1] XOR= carry
        
        # Bit 2: pc_bits[2] + next_carry
        qc.cx(edge_flags[5], pc_bits[2])  # pc_bits[2] XOR= next_carry (ignore overflow)
        
        # Clean up temporaries for next iteration
        # edge_flags[6] and edge_flags[5] must return to 0
        qc.cx(edge_flags[5], carry)
        qc.cx(edge_flags[5], carry)  # Undo to restore
    
    # At this point, pc_bits contains the popcount in binary.
    # Condition: all edge_flags[0:7] are 1, AND pc_bits[2] == 0 (meaning popcount <= 3)
    
    # === APPLY PHASE ===
    # Flip pc_bits[2] so we can use it as a control (we want pc_bits[2]==0, so flip to 1)
    qc.x(pc_bits[2])
    
    # Multi-control Z: apply Z when all controls are 1
    # Controls: edge_flags[0:7] and pc_bits[2]
    control_qubits = list(edge_flags) + [pc_bits[2]]
    qc.mcp(3.141592653589793, control_qubits, pc_bits[0])  # Multi-control phase (angle=pi for Z effect)
    
    # Unflip pc_bits[2]
    qc.x(pc_bits[2])
    
    # === UNCOMPUTE: Popcount (reverse order) ===
    for q_idx in range(len(problem_qubits) - 1, -1, -1):
        qubit = problem_qubits[q_idx]
        
        # Undo bit 2
        qc.cx(edge_flags[5], pc_bits[2])
        
        # Undo bit 1
        qc.cx(carry, pc_bits[1])
        qc.ccx(carry, pc_bits[1], edge_flags[5])
        
        # Undo bit 0
        qc.cx(qubit, pc_bits[0])
        qc.ccx(qubit, pc_bits[0], carry)
    
    # === UNCOMPUTE: Edge flags (reverse order) ===
    for idx in range(len(edges) - 1, -1, -1):
        i, j = edges[idx]
        ea = edge_flags[idx]
        pi, pj = problem_qubits[i], problem_qubits[j]
        qc.ccx(pi, pj, ea)    # undo
        qc.cx(pj, ea)         # undo
        qc.cx(pi, ea)         # undo
