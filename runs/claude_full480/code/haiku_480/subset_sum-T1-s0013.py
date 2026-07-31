import math

def build_oracle(qc, problem_qubits, ancilla_qubits):
    x0, x1, x2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    anc = ancilla_qubits[0]
    
    # Apply phase to state |100>: x0=1, x1=0, x2=0 (selects a[0]=5)
    qc.x(x1)
    qc.x(x2)
    qc.mcx([x0, x1, x2], anc)
    qc.p(math.pi, anc)
    qc.mcx([x0, x1, x2], anc)
    qc.x(x2)
    qc.x(x1)
    
    # Apply phase to state |011>: x0=0, x1=1, x2=1 (selects a[1]+a[2]=2+3)
    qc.x(x0)
    qc.mcx([x0, x1, x2], anc)
    qc.p(math.pi, anc)
    qc.mcx([x0, x1, x2], anc)
    qc.x(x0)
