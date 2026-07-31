from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q = problem_qubits
    a = ancilla_qubits
    
    # Allocate ancillas:
    # a[0]: state1_flag = q0 AND (NOT q1) AND q2 AND (NOT q3)  [state 0101]
    # a[1]: state2_flag = (NOT q0) AND q1 AND (NOT q2) AND q3  [state 1010]
    # a[2]: final_flag = state1_flag OR state2_flag
    # a[3]: temp1 for intermediate computations
    # a[4]: temp2 for intermediate computations
    
    state1_flag = a[0]
    state2_flag = a[1]
    final_flag = a[2]
    temp1 = a[3]
    temp2 = a[4]
    
    # COMPUTE state1_flag = q0 AND (NOT q1) AND q2 AND (NOT q3)
    qc.x(temp1)
    qc.cx(q[1], temp1)      # temp1 = NOT q1
    qc.x(temp2)
    qc.cx(q[3], temp2)      # temp2 = NOT q3
    qc.mcx([q[0], q[2], temp1, temp2], state1_flag)
    
    # UNCOMPUTE state1_flag temporaries
    qc.cx(q[3], temp2)
    qc.x(temp2)
    qc.cx(q[1], temp1)
    qc.x(temp1)
    
    # COMPUTE state2_flag = (NOT q0) AND q1 AND (NOT q2) AND q3
    qc.x(temp1)
    qc.cx(q[0], temp1)      # temp1 = NOT q0
    qc.x(temp2)
    qc.cx(q[2], temp2)      # temp2 = NOT q2
    qc.mcx([temp1, q[1], temp2, q[3]], state2_flag)
    
    # UNCOMPUTE state2_flag temporaries
    qc.cx(q[2], temp2)
    qc.x(temp2)
    qc.cx(q[0], temp1)
    qc.x(temp1)
    
    # COMPUTE final_flag = state1_flag OR state2_flag
    qc.x(temp1)
    qc.cx(state1_flag, temp1)  # temp1 = NOT state1_flag
    qc.x(temp2)
    qc.cx(state2_flag, temp2)  # temp2 = NOT state2_flag
    qc.x(final_flag)           # final_flag = 1
    qc.ccx(temp1, temp2, final_flag)  # final_flag = OR(state1, state2)
    
    # APPLY PHASE: mark the marked states with -1 phase
    qc.z(final_flag)
    
    # UNCOMPUTE final_flag (reverse order)
    qc.ccx(temp1, temp2, final_flag)
    qc.x(final_flag)
    qc.cx(state2_flag, temp2)
    qc.x(temp2)
    qc.cx(state1_flag, temp1)
    qc.x(temp1)
    
    # UNCOMPUTE state2_flag
    qc.mcx([temp1, q[1], temp2, q[3]], state2_flag)
    qc.cx(q[2], temp2)
    qc.x(temp2)
    qc.cx(q[0], temp1)
    qc.x(temp1)
    
    # UNCOMPUTE state1_flag
    qc.mcx([q[0], q[2], temp1, temp2], state1_flag)
    qc.cx(q[3], temp2)
    qc.x(temp2)
    qc.cx(q[1], temp1)
    qc.x(temp1)
