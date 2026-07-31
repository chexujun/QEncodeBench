from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    
    edges = [(0, 2), (0, 3), (1, 2), (1, 3)]
    
    same_color_ancillas = ancilla_qubits[:4]
    final_ancilla = ancilla_qubits[4]
    
    # Compute same_color(u, v) for each edge
    for i, (u, v) in enumerate(edges):
        compute_same_color(qc, problem_qubits, u, v, same_color_ancillas[i])
    
    # Compute AND(NOT same_color[i]) for the constraint satisfaction
    for i in range(4):
        qc.x(same_color_ancillas[i])
    qc.mcx(same_color_ancillas, final_ancilla)
    for i in range(4):
        qc.x(same_color_ancillas[i])
    
    # Apply phase: Z gate to final_ancilla
    qc.z(final_ancilla)
    
    # Uncompute AND(NOT same_color[i])
    for i in range(4):
        qc.x(same_color_ancillas[i])
    qc.mcx(same_color_ancillas, final_ancilla)
    for i in range(4):
        qc.x(same_color_ancillas[i])
    
    # Uncompute same_color bits
    for i, (u, v) in enumerate(edges):
        uncompute_same_color(qc, problem_qubits, u, v, same_color_ancillas[i])


def compute_same_color(qc, problem_qubits, u, v, ancilla):
    u_b0 = problem_qubits[2*u]
    u_b1 = problem_qubits[2*u+1]
    v_b0 = problem_qubits[2*v]
    v_b1 = problem_qubits[2*v+1]
    
    # Compute same_color by checking 6 cases where colors match:
    # (0,0,0,0), (0,0,1,1), (0,1,0,1), (1,0,1,0), (1,1,0,0), (1,1,1,1)
    # Using MCX with negated controls (via X gates), flip ancilla for each true case
    # Result: ancilla = XOR of all true cases = 1 iff colors same
    
    # Case 1: (0,0,0,0)
    qc.x(u_b0)
    qc.x(u_b1)
    qc.x(v_b0)
    qc.x(v_b1)
    qc.mcx([u_b0, u_b1, v_b0, v_b1], ancilla)
    qc.x(u_b0)
    qc.x(u_b1)
    qc.x(v_b0)
    qc.x(v_b1)
    
    # Case 2: (0,0,1,1)
    qc.x(u_b0)
    qc.x(u_b1)
    qc.mcx([u_b0, u_b1, v_b0, v_b1], ancilla)
    qc.x(u_b0)
    qc.x(u_b1)
    
    # Case 3: (0,1,0,1)
    qc.x(u_b0)
    qc.x(v_b0)
    qc.mcx([u_b0, u_b1, v_b0, v_b1], ancilla)
    qc.x(u_b0)
    qc.x(v_b0)
    
    # Case 4: (1,0,1,0)
    qc.x(u_b1)
    qc.x(v_b1)
    qc.mcx([u_b0, u_b1, v_b0, v_b1], ancilla)
    qc.x(u_b1)
    qc.x(v_b1)
    
    # Case 5: (1,1,0,0)
    qc.x(v_b0)
    qc.x(v_b1)
    qc.mcx([u_b0, u_b1, v_b0, v_b1], ancilla)
    qc.x(v_b0)
    qc.x(v_b1)
    
    # Case 6: (1,1,1,1)
    qc.mcx([u_b0, u_b1, v_b0, v_b1], ancilla)


def uncompute_same_color(qc, problem_qubits, u, v, ancilla):
    u_b0 = problem_qubits[2*u]
    u_b1 = problem_qubits[2*u+1]
    v_b0 = problem_qubits[2*v]
    v_b1 = problem_qubits[2*v+1]
    
    # Reverse compute_same_color in reverse order
    # Case 6
    qc.mcx([u_b0, u_b1, v_b0, v_b1], ancilla)
    
    # Case 5
    qc.x(v_b0)
    qc.x(v_b1)
    qc.mcx([u_b0, u_b1, v_b0, v_b1], ancilla)
    qc.x(v_b0)
    qc.x(v_b1)
    
    # Case 4
    qc.x(u_b1)
    qc.x(v_b1)
    qc.mcx([u_b0, u_b1, v_b0, v_b1], ancilla)
    qc.x(u_b1)
    qc.x(v_b1)
    
    # Case 3
    qc.x(u_b0)
    qc.x(v_b0)
    qc.mcx([u_b0, u_b1, v_b0, v_b1], ancilla)
    qc.x(u_b0)
    qc.x(v_b0)
    
    # Case 2
    qc.x(u_b0)
    qc.x(u_b1)
    qc.mcx([u_b0, u_b1, v_b0, v_b1], ancilla)
    qc.x(u_b0)
    qc.x(u_b1)
    
    # Case 1
    qc.x(u_b0)
    qc.x(u_b1)
    qc.x(v_b0)
    qc.x(v_b1)
    qc.mcx([u_b0, u_b1, v_b0, v_b1], ancilla)
    qc.x(u_b0)
    qc.x(u_b1)
    qc.x(v_b0)
    qc.x(v_b1)
