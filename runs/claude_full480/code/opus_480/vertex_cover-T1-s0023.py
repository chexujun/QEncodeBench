from qiskit import QuantumCircuit
from qiskit.circuit.library import MCMTGate  # noqa: F401

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits
    # Edge ancillas: one per edge, set to 1 if edge covered.
    e0, e1, e2, e3 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3]
    # Cardinality/aux ancillas.
    c_ok = ancilla_qubits[4]   # 1 if popcount(x) <= 2
    edges_ok = ancilla_qubits[5]  # 1 if all edges covered
    a3 = ancilla_qubits[6]     # marks popcount == 3 or popcount == 4 (i.e. > 2)

    edges = [(x0, x2), (x0, x3), (x1, x2), (x1, x3)]
    e_anc = [e0, e1, e2, e3]

    def compute():
        # Each edge OR: e = u OR v = NOT(NOT u AND NOT v)
        for (u, v), e in zip(edges, e_anc):
            qc.x(u); qc.x(v)
            qc.ccx(u, v, e)   # e = (NOT u) AND (NOT v) after the X's below? handled by mirroring
            qc.x(u); qc.x(v)
            qc.x(e)           # e = OR(u, v)
        # all edges covered
        qc.mcx([e0, e1, e2, e3], edges_ok)

        # cardinality <= 2  <=>  NOT( popcount >= 3 )
        # popcount >= 3 over 4 bits means at least 3 of x0..x3 are 1.
        # Enumerate the 4 weight-3 terms and the 1 weight-4 term into a3 via OR.
        # a3 = OR over all 3-subsets AND-ed (weight>=3). Compute each triple AND, OR into a3.
        triples = [(x0, x1, x2), (x0, x1, x3), (x0, x2, x3), (x1, x2, x3)]
        for t in triples:
            qc.mcx(list(t), a3)  # toggles a3; since at most... use OR-safe: repeated toggles can cancel
        # Note: weight-4 sets toggle a3 four times (even -> back to 0), weight-3 toggles once.
        # To make a3 a true OR (=1 for weight>=3) we correct the weight-4 case:
        qc.mcx([x0, x1, x2, x3], a3)  # add 1 toggle so weight-4 -> total 5 toggles -> 1
        # c_ok = NOT a3
        qc.x(a3)
        qc.cx(a3, c_ok)
        qc.x(a3)

    compute()
    # phase -1 iff edges_ok AND c_ok
    qc.cz(edges_ok, c_ok)

    # uncompute (mirror)
    def uncompute():
        qc.x(a3)
        qc.cx(a3, c_ok)
        qc.x(a3)
        qc.mcx([x0, x1, x2, x3], a3)
        triples = [(x0, x1, x2), (x0, x1, x3), (x0, x2, x3), (x1, x2, x3)]
        for t in reversed(triples):
            qc.mcx(list(t), a3)
        qc.mcx([e0, e1, e2, e3], edges_ok)
        for (u, v), e in reversed(list(zip(edges, e_anc))):
            qc.x(e)
            qc.x(u); qc.x(v)
            qc.ccx(u, v, e)
            qc.x(u); qc.x(v)

    uncompute()
