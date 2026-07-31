from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # pattern = "0???": f(x)=1 iff s_0 == 0, i.e. problem_qubits[0] == |0>.
    # Phase -1 on states with x_0 = 0: apply X, Z, X on that qubit.
    q0 = problem_qubits[0]
    qc.x(q0)
    qc.z(q0)
    qc.x(q0)
