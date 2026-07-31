from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Graph: vertices 0,1,2,3; edges (0,1), (0,2), (0,3)
    # Vertex v uses problem_qubits[2v:2v+2] for color code (b0, b1)
    # f(x) = 1 iff all edges connect vertices of different colors
    
    edges = [(0, 1), (0, 2), (0, 3)]
    edge_results = ancilla_qubits[0:3]
    final_result = ancilla_qubits[3]
    temp_base = 4
    
    # Compute diff_color for each edge
    for i, (u, v) in enumerate(edges):
        compute_colors_differ(qc, problem_qubits, u, v, edge_results[i],
                            ancilla_qubits[temp_base:temp_base+10])
    
    # AND all three edge constraints: result = e0 AND e1 AND e2
    temp_and = ancilla_qubits[temp_base]
    qc.ccx(edge_results[0], edge_results[1], temp_and)
    qc.ccx(temp_and, edge_results[2], final_result)
    qc.ccx(edge_results[0], edge_results[1], temp_and)
    
    # Apply phase flip to mark solutions
    qc.z(final_result)
    
    # Uncompute the AND
    qc.ccx(edge_results[0], edge_results[1], temp_and)
    qc.ccx(temp_and, edge_results[2], final_result)
    qc.ccx(edge_results[0], edge_results[1], temp_and)
    
    # Uncompute edge constraints in reverse order
    for i, (u, v) in enumerate(reversed(edges)):
        idx = len(edges) - 1 - i
        compute_colors_differ(qc, problem_qubits, edges[idx][0], edges[idx][1],
                            edge_results[idx], ancilla_qubits[temp_base:temp_base+10])

def compute_colors_differ(qc, problem_qubits, u, v, result, temps):
    # Determines if colors of vertices u and v differ
    # Colors are same iff: (codes identical) OR (both in {0,3})
    # Two 2-bit codes are in {0,3} iff both bits match (00 or 11)
    
    b0_u, b1_u = problem_qubits[2*u], problem_qubits[2*u+1]
    b0_v, b1_v = problem_qubits[2*v], problem_qubits[2*v+1]
    
    xnor_b0, xnor_b1 = temps[0], temps[1]
    both_bits_equal = temps[2]
    u_in_special = temps[3]
    v_in_special = temps[4]
    both_special = temps[5]
    same_color = temps[6]
    
    # XNOR(b0_u, b0_v): 1 iff b0_u == b0_v
    qc.cx(b0_u, xnor_b0)
    qc.cx(b0_v, xnor_b0)
    qc.x(xnor_b0)
    
    # XNOR(b1_u, b1_v)
    qc.cx(b1_u, xnor_b1)
    qc.cx(b1_v, xnor_b1)
    qc.x(xnor_b1)
    
    # both_bits_equal = (b0 equal) AND (b1 equal)
    qc.ccx(xnor_b0, xnor_b1, both_bits_equal)
    
    # u_in_special: 1 iff both u bits equal (00 or 11)
    # = XNOR(b0_u, b1_u)
    qc.cx(b0_u, u_in_special)
    qc.cx(b1_u, u_in_special)
    qc.x(u_in_special)
    
    # v_in_special: XNOR(b0_v, b1_v)
    qc.cx(b0_v, v_in_special)
    qc.cx(b1_v, v_in_special)
    qc.x(v_in_special)
    
    # both_special = u_in_special AND v_in_special
    qc.ccx(u_in_special, v_in_special, both_special)
    
    # same_color = both_bits_equal OR both_special
    qc.cx(both_bits_equal, same_color)
    qc.cx(both_special, same_color)
    
    # result = NOT same_color (i.e., colors differ)
    qc.x(same_color)
    qc.cx(same_color, result)
    qc.x(same_color)
    
    # Uncompute in reverse
    qc.cx(both_special, same_color)
    qc.cx(both_bits_equal, same_color)
    
    qc.ccx(u_in_special, v_in_special, both_special)
    
    qc.cx(b0_v, v_in_special)
    qc.cx(b1_v, v_in_special)
    qc.x(v_in_special)
    
    qc.cx(b0_u, u_in_special)
    qc.cx(b1_u, u_in_special)
    qc.x(u_in_special)
    
    qc.ccx(xnor_b0, xnor_b1, both_bits_equal)
    
    qc.cx(b1_v, xnor_b1)
    qc.x(xnor_b1)
    qc.cx(b1_u, xnor_b1)
    
    qc.cx(b0_v, xnor_b0)
    qc.x(xnor_b0)
    qc.cx(b0_u, xnor_b0)
