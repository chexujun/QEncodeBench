from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    edges = [(0,4), (0,5), (1,3), (2,3), (2,4), (3,4), (4,5)]
    
    # Allocate ancillas
    a_temp1, a_temp2 = ancilla_qubits[0], ancilla_qubits[1]
    a_edge = list(ancilla_qubits[2:9])  # 7 ancillas for edge coverage
    a_all_edges = ancilla_qubits[9]     # 1 ancilla for "all edges covered"
    
    # ===== COMPUTE PHASE =====
    
    # Step 1: Compute edge coverage (OR for each edge)
    for i, (u, v) in enumerate(edges):
        # OR(x_u, x_v) into a_edge[i]: cx, cx, ccx formula
        qc.cx(problem_qubits[u], a_edge[i])
        qc.cx(problem_qubits[v], a_edge[i])
        qc.ccx(problem_qubits[u], problem_qubits[v], a_edge[i])
    
    # Step 2: AND all edge coverages
    qc.cx(a_edge[0], a_all_edges)
    for i in range(1, 7):
        qc.ccx(a_all_edges, a_edge[i], a_temp1)
        qc.cx(a_temp1, a_all_edges)
        qc.ccx(a_all_edges, a_edge[i], a_temp1)
    
    # Step 3: Check size <= 3 (equivalently, NOT(size >= 4))
    # Compute "size >= 4" by checking if any 4-subset has all bits set
    # Reuse a_temp1 as accumulator for "at_least_4"
    for i0 in range(6):
        for i1 in range(i0+1, 6):
            for i2 in range(i1+1, 6):
                for i3 in range(i2+1, 6):
                    # Compute AND(x[i0], x[i1], x[i2], x[i3]) and OR into a_temp1
                    qc.ccx(problem_qubits[i0], problem_qubits[i1], a_temp2)
                    qc.ccx(problem_qubits[i2], problem_qubits[i3], a_edge[0])
                    qc.ccx(a_temp2, a_edge[0], a_edge[1])
                    # OR a_edge[1] into a_temp1
                    qc.cx(a_edge[1], a_temp1)
                    qc.cx(a_temp1, a_edge[1])
                    qc.ccx(a_temp1, a_edge[1], a_edge[2])
                    qc.cx(a_edge[2], a_temp1)
                    qc.ccx(a_temp1, a_edge[1], a_edge[2])
                    qc.cx(a_edge[1], a_temp1)
                    # Uncompute
                    qc.ccx(a_temp2, a_edge[0], a_edge[1])
                    qc.ccx(problem_qubits[i2], problem_qubits[i3], a_edge[0])
                    qc.ccx(problem_qubits[i0], problem_qubits[i1], a_temp2)
    
    # Step 4: Combine: final = all_edges AND NOT(at_least_4)
    qc.x(a_temp1)  # Flip to get NOT(size >= 4)
    qc.ccx(a_all_edges, a_temp1, a_temp2)
    qc.cx(a_temp2, a_all_edges)
    qc.ccx(a_all_edges, a_temp1, a_temp2)
    qc.x(a_temp1)  # Flip back
    
    # ===== APPLY PHASE =====
    qc.z(a_all_edges)
    
    # ===== UNCOMPUTE =====
    qc.x(a_temp1)
    qc.ccx(a_all_edges, a_temp1, a_temp2)
    qc.cx(a_temp2, a_all_edges)
    qc.ccx(a_all_edges, a_temp1, a_temp2)
    qc.x(a_temp1)
    
    for i0 in range(5, -1, -1):
        for i1 in range(5, i0, -1):
            for i2 in range(5, i1, -1):
                for i3 in range(5, i2, -1):
                    qc.cx(a_edge[1], a_temp1)
                    qc.cx(a_temp1, a_edge[1])
                    qc.ccx(a_temp1, a_edge[1], a_edge[2])
                    qc.cx(a_edge[2], a_temp1)
                    qc.ccx(a_temp1, a_edge[1], a_edge[2])
                    qc.cx(a_edge[1], a_temp1)
                    qc.ccx(a_temp2, a_edge[0], a_edge[1])
                    qc.ccx(problem_qubits[i2], problem_qubits[i3], a_edge[0])
                    qc.ccx(problem_qubits[i0], problem_qubits[i1], a_temp2)
    
    for i in range(6, 0, -1):
        qc.ccx(a_all_edges, a_edge[i], a_temp1)
        qc.cx(a_temp1, a_all_edges)
        qc.ccx(a_all_edges, a_edge[i], a_temp1)
    qc.cx(a_edge[0], a_all_edges)
    
    for i in range(6, -1, -1):
        u, v = edges[i]
        qc.ccx(problem_qubits[u], problem_qubits[v], a_edge[i])
        qc.cx(problem_qubits[v], a_edge[i])
        qc.cx(problem_qubits[u], a_edge[i])
