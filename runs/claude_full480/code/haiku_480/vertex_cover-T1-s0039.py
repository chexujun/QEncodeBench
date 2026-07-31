from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    p0, p1, p2, p3 = problem_qubits
    a0, a1, a2, a3, a4, a5 = ancilla_qubits
    
    # Identify valid vertex covers of size ≤ 2 for the graph with edges (0,2), (1,2), (1,3)
    # Valid covers: {0,1}, {1,2}, {2,3} corresponding to states |3>, |6>, |12>
    # State |3>: p0=1, p1=1, p2=0, p3=0
    qc.mcx([p0, p1, p2, p3], a3, ctrl_state='1100')
    # State |6>: p0=0, p1=1, p2=1, p3=0
    qc.mcx([p0, p1, p2, p3], a4, ctrl_state='0110')
    # State |12>: p0=0, p1=0, p2=1, p3=1
    qc.mcx([p0, p1, p2, p3], a5, ctrl_state='0011')
    
    # OR a3 and a4 into a2
    qc.cx(a3, a2)
    qc.cx(a4, a2)
    qc.ccx(a3, a4, a2)
    
    # OR result with a5 into a1
    qc.cx(a2, a1)
    qc.cx(a5, a1)
    qc.ccx(a2, a5, a1)
    
    # Apply phase -1 if any valid state is marked
    qc.z(a1)
    
    # Uncompute ancillas (reverse order, reverse operations)
    qc.ccx(a2, a5, a1)
    qc.cx(a5, a1)
    qc.cx(a2, a1)
    qc.ccx(a3, a4, a2)
    qc.cx(a4, a2)
    qc.cx(a3, a2)
    qc.mcx([p0, p1, p2, p3], a5, ctrl_state='0011')
    qc.mcx([p0, p1, p2, p3], a4, ctrl_state='0110')
    qc.mcx([p0, p1, p2, p3], a3, ctrl_state='1100')
