from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    cl_anc = ancilla_qubits[:10]   # one ancilla per clause
    out = ancilla_qubits[10]       # final phase ancilla

    # Each clause: (literals). polarity True means positive literal (x_i),
    # False means negated (NOT x_i). A clause is satisfied unless ALL its
    # literals are false.
    clauses = [
        [(0, True),  (6, True),  (7, True)],
        [(1, False), (3, False), (7, True)],
        [(1, True),  (3, False), (4, True)],
        [(0, True),  (6, True),  (7, False)],
        [(2, False), (5, False), (7, True)],
        [(1, True),  (5, False), (6, False)],
        [(1, False), (3, True),  (6, True)],
        [(1, False), (4, True),  (5, False)],
        [(4, True),  (5, False), (7, False)],
        [(2, False), (4, False), (7, False)],
    ]

    def compute_clauses():
        for ci, clause in enumerate(clauses):
            ctrls = [lit[0] for lit in clause]
            # Flip qubits so that "clause unsatisfied" corresponds to all ctrls = 1.
            # A positive literal x_i is false when x_i = 0 -> X it to get 1.
            # A negative literal is false when x_i = 1 -> leave as is.
            for qi, pol in clause:
                if pol:
                    qc.x(x[qi])
            # clause ancilla starts |0>; set it to 1 when clause is UNsatisfied
            qc.mcx(ctrls, cl_anc[ci])
            # Flip clause ancilla so that 1 = satisfied
            qc.x(cl_anc[ci])
            # restore problem qubits
            for qi, pol in clause:
                if pol:
                    qc.x(x[qi])

    # compute all clause satisfaction flags
    compute_clauses()

    # out = AND of all clause flags (formula satisfied)
    qc.mcx(cl_anc, out)
    # apply phase
    qc.z(out)
    # uncompute out
    qc.mcx(cl_anc, out)

    # uncompute clause flags (mirror)
    for ci in reversed(range(len(clauses))):
        clause = clauses[ci]
        ctrls = [lit[0] for lit in clause]
        for qi, pol in clause:
            if pol:
                qc.x(x[qi])
        qc.x(cl_anc[ci])
        qc.mcx(ctrls, cl_anc[ci])
        for qi, pol in clause:
            if pol:
                qc.x(x[qi])
