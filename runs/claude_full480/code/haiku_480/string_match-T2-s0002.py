from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pq = problem_qubits  # 5 qubits for binary text
    aq = ancilla_qubits  # 4 ancillas
    
    # === Compute match flags for each offset ===
    
    # Offset 0: pattern "110" matches if s_0=1, s_1=1, s_2=0
    # Compute into aq[0] using: (pq[0] AND pq[1] AND NOT pq[2])
    qc.x(pq[2])
    qc.ccx(pq[0], pq[1], aq[3])
    qc.ccx(pq[2], aq[3], aq[0])
    qc.ccx(pq[0], pq[1], aq[3])
    qc.x(pq[2])
    
    # Offset 1: pattern "110" matches if s_1=1, s_2=1, s_3=0
    # Compute into aq[1]
    qc.x(pq[3])
    qc.ccx(pq[1], pq[2], aq[3])
    qc.ccx(pq[3], aq[3], aq[1])
    qc.ccx(pq[1], pq[2], aq[3])
    qc.x(pq[3])
    
    # Offset 2: pattern "110" matches if s_2=1, s_3=1, s_4=0
    # Compute into aq[2]
    qc.x(pq[4])
    qc.ccx(pq[2], pq[3], aq[3])
    qc.ccx(pq[4], aq[3], aq[2])
    qc.ccx(pq[2], pq[3], aq[3])
    qc.x(pq[4])
    
    # === Apply phase using inclusion-exclusion for OR ===
    # Z^(a OR b OR c) = Z^a * Z^b * Z^c * Z^(a AND b) * Z^(a AND c) * Z^(b AND c) * Z^(a AND b AND c)
    # Each term applies a phase gate conditioned on ancilla flags
    
    qc.cz(aq[0], pq[0])
    qc.cz(aq[1], pq[0])
    qc.cz(aq[2], pq[0])
    qc.ccz(aq[0], aq[1], pq[0])
    qc.ccz(aq[0], aq[2], pq[0])
    qc.ccz(aq[1], aq[2], pq[0])
    
    # 3-controlled Z: decomposed using CCX + CCZ + CCX
    qc.ccx(aq[0], aq[1], aq[3])
    qc.ccz(aq[3], aq[2], pq[0])
    qc.ccx(aq[0], aq[1], aq[3])
    
    # === Uncompute flags (mirror of compute) ===
    
    # Uncompute offset 2
    qc.x(pq[4])
    qc.ccx(pq[2], pq[3], aq[3])
    qc.ccx(pq[4], aq[3], aq[2])
    qc.ccx(pq[2], pq[3], aq[3])
    qc.x(pq[4])
    
    # Uncompute offset 1
    qc.x(pq[3])
    qc.ccx(pq[1], pq[2], aq[3])
    qc.ccx(pq[3], aq[3], aq[1])
    qc.ccx(pq[1], pq[2], aq[3])
    qc.x(pq[3])
    
    # Uncompute offset 0
    qc.x(pq[2])
    qc.ccx(pq[0], pq[1], aq[3])
    qc.ccx(pq[2], aq[3], aq[0])
    qc.ccx(pq[0], pq[1], aq[3])
    qc.x(pq[2])
