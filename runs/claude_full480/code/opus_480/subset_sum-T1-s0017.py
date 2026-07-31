from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Subset-sum: a = [1, 4, 6], target T = 5.
    # Subsets summing to 5: {1,4} -> bits x0=1, x1=1, x2=0.
    # No other subset of {1,4,6} sums to 5.
    # So f(x) = 1  iff  x0=1 AND x1=1 AND x2=0.
    q0, q1, q2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]

    # Flip q2 so the condition becomes all-ones on (q0, q1, q2').
    qc.x(q2)
    # Phase -1 exactly when q0=1, q1=1, q2'=1 (i.e. q0=1,q1=1,q2=0).
    qc.h(q2)
    qc.ccx(q0, q1, q2)
    qc.h(q2)
    # Restore q2.
    qc.x(q2)
