from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # The completed 3x3 Latin square requires:
    # - Free cell 0 (position (0,1)) = 0
    # - Free cell 1 (position (1,2)) = 1
    #
    # Encoding: cell j uses qubits [2j, 2j+1] 
    # Code = b0 + 2*b1; decoding: 00→0, 01→1, 10→2, 11→0
    #
    # Constraint checks:
    # - Value 0: b0 == b1 (codes 00 or 11)
    # - Value 1: b0==1 AND b1==0 (code 01)
    
    p0, p1 = problem_qubits[0], problem_qubits[1]
    p2, p3 = problem_qubits[2], problem_qubits[3]
    
    a_eq = ancilla_qubits[0]
    a_cond2 = ancilla_qubits[1]
    a_result = ancilla_qubits[2]
    
    # Compute: a_eq = (p0 == p1)
    qc.cx(p0, a_eq)
    qc.cx(p1, a_eq)
    qc.x(a_eq)
    
    # Compute: a_cond2 = (p2==1 AND p3==0)
    qc.x(p3)
    qc.ccx(p2, p3, a_cond2)
    qc.x(p3)
    
    # Combine constraints
    qc.ccx(a_eq, a_cond2, a_result)
    
    # Apply phase -1 iff both conditions hold
    qc.z(a_result)
    
    # Uncompute
    qc.ccx(a_eq, a_cond2, a_result)
    
    qc.x(p3)
    qc.ccx(p2, p3, a_cond2)
    qc.x(p3)
    
    qc.x(a_eq)
    qc.cx(p1, a_eq)
    qc.cx(p0, a_eq)
