from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # The unique solution is:
    # Cell (0,0) = 0 (code 00), Cell (0,1) = 2 (code 10),
    # Cell (1,1) = 0 (code 00), Cell (2,1) = 1 (code 01)
    # 
    # Bit representation: q = [0, 0, 0, 1, 0, 0, 1, 0]
    # Constraint: NOT q[0] AND NOT q[1] AND q[2] AND NOT q[3] 
    #             AND NOT q[4] AND NOT q[5] AND q[6] AND NOT q[7]
    
    q = problem_qubits
    a = ancilla_qubits
    
    # Prepare: flip bits to convert NOT conditions to positive checks
    # After flips, we check if all bits are 1
    qc.x(q[0])
    qc.x(q[1])
    qc.x(q[3])
    qc.x(q[4])
    qc.x(q[5])
    qc.x(q[7])
    
    # Compute: use multi-controlled X to compute AND into a[0]
    # a[0] becomes 1 iff all problem_qubits are 1 (after flips)
    qc.mcx(q, a[0], a[1:], mode='basic')
    
    # Phase: apply Z gate to encode phase -1 when a[0] = 1
    qc.z(a[0])
    
    # Uncompute: reverse the AND computation, returning all ancillas to |0>
    qc.mcx(q, a[0], a[1:], mode='basic')
    
    # Flip back: restore problem qubits to original state
    qc.x(q[7])
    qc.x(q[5])
    qc.x(q[4])
    qc.x(q[3])
    qc.x(q[1])
    qc.x(q[0])
