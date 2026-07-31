from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits, ancilla_qubits):
    # pattern = "000?": positions 0,1,2 must be 0; position 3 is wildcard.
    # f(x)=1 iff s0=0 and s1=0 and s2=0.
    a = ancilla_qubits[0]
    controls = [problem_qubits[0], problem_qubits[1], problem_qubits[2]]
    # compute AND of NOT(s0),NOT(s1),NOT(s2) into ancilla a
    qc.x(controls[0]); qc.x(controls[1]); qc.x(controls[2])
    qc.mcx(controls, a)
    qc.z(a)
    qc.mcx(controls, a)
    qc.x(controls[0]); qc.x(controls[1]); qc.x(controls[2])
