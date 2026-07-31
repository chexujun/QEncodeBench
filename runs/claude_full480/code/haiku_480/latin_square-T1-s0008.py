from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q0, q1, q2, q3 = problem_qubits[:4]
    aux_0, aux_1, temp1, temp2, pred = ancilla_qubits[:5]
    
    # Compute NOT q0
    qc.cx(q0, aux_0)
    qc.x(aux_0)
    
    # Compute NOT q2
    qc.cx(q2, aux_1)
    qc.x(aux_1)
    
    # Compute AND of q1, aux_0, aux_1, q3 into pred
    qc.ccx(q1, aux_0, temp1)
    qc.ccx(temp1, aux_1, temp2)
    qc.ccx(temp2, q3, pred)
    
    # Apply Z to mark the state
    qc.z(pred)
    
    # Uncompute (in reverse order)
    qc.ccx(temp2, q3, pred)
    qc.ccx(temp1, aux_1, temp2)
    qc.ccx(q1, aux_0, temp1)
    
    # Uncompute NOT q2
    qc.x(aux_1)
    qc.cx(q2, aux_1)
    
    # Uncompute NOT q0
    qc.x(aux_0)
    qc.cx(q0, aux_0)
