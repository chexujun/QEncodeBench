from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # pattern = "?110?": position 0 '?', 1 '1', 2 '1', 3 '0', 4 '?'
    # Match iff s1==1 and s2==1 and s3==0.
    q1 = problem_qubits[1]
    q2 = problem_qubits[2]
    q3 = problem_qubits[3]
    # Flip s3 so that the "0" requirement becomes a "1" control.
    qc.x(q3)
    # Phase -1 iff q1=1, q2=1, q3(after flip)=1 using a controlled-Z style multi-control.
    qc.h(q3)
    qc.ccx(q1, q2, q3)
    qc.h(q3)
    # Uncompute the X flip.
    qc.x(q3)
