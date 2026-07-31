from qiskit import QuantumCircuit
from math import pi

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    x0, x1, x2, x3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]
    e = ancilla_qubits[0:4]      # edge-cover ancillas
    ok = ancilla_qubits[4]       # all-edges-covered flag
    c = ancilla_qubits[5]        # count<=2 flag
    r = ancilla_qubits[6]        # final predicate flag

    # ---- compute: edge coverage (edge covered iff at least one endpoint = 1) ----
    # e[k] = OR(u,v) = NOT( (NOT u) AND (NOT v) ). Compute e[k]=1 iff covered.
    edges = [(x0, x1), (x0, x2), (x0, x3), (x2, x3)]
    for k, (u, v) in enumerate(edges):
        qc.x(u); qc.x(v)
        qc.x(e[k])
        qc.ccx(u, v, e[k])   # e[k] = 1 XOR (nu AND nv) = NOT(nu AND nv) = OR(u,v)
        qc.x(u); qc.x(v)

    # ok = AND of all e[k]  (all edges covered)
    qc.mcx([e[0], e[1], e[2], e[3]], ok)

    # ---- compute: count of ones <= 2, i.e. NOT(three-or-more ones) ----
    # For 4 bits, |x|>=3 iff some triple is all ones. Triples:
    triples = [(x0, x1, x2), (x0, x1, x3), (x0, x2, x3), (x1, x2, x3)]
    # c starts |0>; set c=1 if any triple all-ones (i.e. count>=3), then invert.
    for (a, b, d) in triples:
        qc.mcx([a, b, d], c)   # for count exactly 3, one triple fires; for count 4, an odd number fire
    # count==4: all four triples fire -> parity 0 -> c=0 incorrectly. Fix with 4-way term.
    qc.mcx([x0, x1, x2, x3], c)  # fires once when count==4, restoring c=1
    # Now c = 1 iff count>=3. We want count<=2 => use NOT c.
    qc.x(c)  # c = 1 iff count<=2

    # ---- combine: r = ok AND c ----
    qc.ccx(ok, c, r)

    # ---- phase ----
    qc.z(r)

    # ---- uncompute (mirror) ----
    qc.ccx(ok, c, r)
    qc.x(c)
    qc.mcx([x0, x1, x2, x3], c)
    for (a, b, d) in reversed(triples):
        qc.mcx([a, b, d], c)
    qc.mcx([e[0], e[1], e[2], e[3]], ok)
    for k, (u, v) in reversed(list(enumerate(edges))):
        qc.x(u); qc.x(v)
        qc.ccx(u, v, e[k])
        qc.x(e[k])
        qc.x(u); qc.x(v)
