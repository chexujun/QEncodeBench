from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Qubit assignment
    eq_b0 = ancilla_qubits[0]
    eq_b1 = ancilla_qubits[1]
    edge_mono = ancilla_qubits[2]
    temp_or = ancilla_qubits[3]
    mono_check = ancilla_qubits[4]
    work_phase = ancilla_qubits[5]
    
    # Vertex qubit assignments (2 qubits per vertex)
    def get_vertex_qubits(v):
        return (problem_qubits[2*v], problem_qubits[2*v + 1])
    
    # Edges in the graph
    edges = [(0, 2), (0, 3), (0, 4), (1, 4), (3, 4)]
    
    # Initialize work_phase to |1>
    qc.x(work_phase)
    
    # Compute monochromatic check for each edge
    for u, v in edges:
        b0_u, b1_u = get_vertex_qubits(u)
        b0_v, b1_v = get_vertex_qubits(v)
        
        # Compute eq_b0 = (b0_u == b0_v)
        qc.cnot(b0_u, eq_b0)
        qc.cnot(b0_v, eq_b0)
        qc.x(eq_b0)
        
        # Compute eq_b1 = (b1_u == b1_v)
        qc.cnot(b1_u, eq_b1)
        qc.cnot(b1_v, eq_b1)
        qc.x(eq_b1)
        
        # Compute edge_mono = eq_b0 AND eq_b1
        qc.ccx(eq_b0, eq_b1, edge_mono)
        
        # OR edge_mono into mono_check
        qc.x(mono_check)
        qc.ccx(edge_mono, mono_check, temp_or)
        qc.x(mono_check)
        qc.cx(temp_or, mono_check)
    
    # Apply phase when mono_check == 0 (all edges properly colored)
    qc.cx(mono_check, work_phase)
    qc.z(work_phase)
    qc.cx(mono_check, work_phase)
    
    # Uncompute in reverse order
    for u, v in reversed(edges):
        b0_u, b1_u = get_vertex_qubits(u)
        b0_v, b1_v = get_vertex_qubits(v)
        
        # Uncompute OR
        qc.x(mono_check)
        qc.ccx(edge_mono, mono_check, temp_or)
        qc.x(mono_check)
        qc.cx(temp_or, mono_check)
        
        # Uncompute edge_mono
        qc.ccx(eq_b0, eq_b1, edge_mono)
        
        # Uncompute eq_b1
        qc.x(eq_b1)
        qc.cnot(b1_v, eq_b1)
        qc.cnot(b1_u, eq_b1)
        
        # Uncompute eq_b0
        qc.x(eq_b0)
        qc.cnot(b0_v, eq_b0)
        qc.cnot(b0_u, eq_b0)
    
    # Reset work_phase to |0>
    qc.x(work_phase)
