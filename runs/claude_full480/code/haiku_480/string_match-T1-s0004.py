from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a0 = ancilla_qubits[0]
    a1 = ancilla_qubits[1]
    
    # Compute: check if first 3 qubits are 0 using compute-phase-uncompute
    qc.x(problem_qubits[0])
    qc.x(problem_qubits[1])
    qc.ccx(problem_qubits[0], problem_qubits[1], a0)
    qc.x(problem_qubits[2])
    qc.ccx(a0, problem_qubits[2], a1)
    
    # Phase: apply -1 iff a1=1 (i.e., iff all first 3 bits were 0)
    qc.z(a1)
    
    # Uncompute (mirror of compute)
    qc.ccx(a0, problem_qubits[2], a1)
    qc.x(problem_qubits[2])
    qc.ccx(problem_qubits[0], problem_qubits[1], a0)
    qc.x(problem_qubits[0])
    qc.x(problem_qubits[1])
