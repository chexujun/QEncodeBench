import math

def build_oracle(qc, problem_qubits, ancilla_qubits):
    pq = problem_qubits
    aq = ancilla_qubits
    
    # Compute NOT f_i into aq[i+1] for each offset i
    for i in range(5):
        qc.mcx([pq[i], pq[i+1], pq[i+2], pq[i+3]], aq[i+1], ctrl_state='1010')
        qc.x(aq[i+1])
    
    # Compute AND of all NOT f_i
    qc.mcx([aq[1], aq[2], aq[3], aq[4], aq[5]], aq[0])
    
    # Flip to get OR: aq[0] = f_0 OR f_1 OR ... OR f_4
    qc.x(aq[0])
    
    # Apply phase: P(π) gives -1 when qubit is |1>
    qc.p(math.pi, aq[0])
    
    # Uncompute in reverse order
    qc.x(aq[0])
    qc.mcx([aq[1], aq[2], aq[3], aq[4], aq[5]], aq[0])
    
    for i in range(4, -1, -1):
        qc.x(aq[i+1])
        qc.mcx([pq[i], pq[i+1], pq[i+2], pq[i+3]], aq[i+1], ctrl_state='1010')
