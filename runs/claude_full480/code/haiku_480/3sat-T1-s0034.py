from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    x0, x1, x2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    a0 = ancilla_qubits[0]
    
    # Identify satisfying assignments by enumerating all 8 states:
    # 000: all clauses true ✓
    # 001: clause 3 false ✗
    # 010: all clauses true ✓
    # 011: all clauses true ✓
    # 100: clause 2 false ✗
    # 101: clause 1 false ✗
    # 110: clause 4 false ✗
    # 111: all clauses true ✓
    
    # Compute phase oracle by toggling a0 on each satisfying state
    qc.mcx([x0, x1, x2], a0, ctrl_state="000")
    qc.mcx([x0, x1, x2], a0, ctrl_state="010")
    qc.mcx([x0, x1, x2], a0, ctrl_state="011")
    qc.mcx([x0, x1, x2], a0, ctrl_state="111")
    
    # Apply phase gate
    qc.z(a0)
    
    # Uncompute (restore ancilla to |0>)
    qc.mcx([x0, x1, x2], a0, ctrl_state="111")
    qc.mcx([x0, x1, x2], a0, ctrl_state="011")
    qc.mcx([x0, x1, x2], a0, ctrl_state="010")
    qc.mcx([x0, x1, x2], a0, ctrl_state="000")
