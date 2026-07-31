import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits
    edges = [(0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]

    edge_anc = ancilla_qubits[0:5]      # one ancilla per edge (covered flag)
    cnt_anc = ancilla_qubits[5:8]       # 3 ancillas: popcount / weight bits

    p = [x0, x1, x2, x3]

    # ---- compute: edge-covered flags ----
    # edge covered iff (xu OR xv) == 1  ->  flag = NOT( (NOT xu) AND (NOT xv) )
    for (u, v), a in zip(edges, edge_anc):
        qc.x(p[u])
        qc.x(p[v])
        qc.ccx(p[u], p[v], a)   # a = (NOT xu)AND(NOT xv) after the X's -> a=1 if edge UNcovered
        qc.x(p[u])
        qc.x(p[v])
        qc.x(a)                 # a = 1 iff edge covered

    # ---- compute: weight <= 2  (i.e. NOT(all-of-any-3-subset)=... ) ----
    # size <= 2 is FALSE only when 3 or 4 vertices are chosen.
    # We compute a flag w = 1 iff weight <= 2, using ancillas.
    # weight >= 3 iff at least one of the C(4,3)=4 triples is all-ones,
    # OR all four are ones (covered by the triples anyway).
    c0, c1, w = cnt_anc  # c0,c1 scratch; w = weight-ok flag
    triples = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
    # c0 = OR over triples of (all three ones).  Build via toggling:
    # Use c0 as "at least one triple all-ones" using inclusion through CCX+parity is tricky;
    # instead compute directly: c0 = 1 iff weight>=3.
    # weight>=3  <=>  (x0x1x2)+(x0x1x3)+(x0x2x3)+(x1x2x3) >= 1.
    # Only when exactly 3 ones: exactly one triple true. When 4 ones: all four true (parity 0!).
    # So parity fails; use explicit OR via De Morgan on c0 flag with mcx accumulation:
    # Set c0=1 if any triple all-ones by CX-from-a-temporary is complex; use direct threshold.
    #
    # Simpler exact approach: w = 1 iff weight<=2.
    # weight<=2 is FALSE iff (>=3 ones). Enumerate the "bad" high-weight condition as:
    #   bad = (x0&x1&x2)|(x0&x1&x3)|(x0&x2&x3)|(x1&x2&x3)
    # Compute bad into c0 using OR accumulation with an extra scratch c1.
    for t in triples:
        qc.ccx(p[t[0]], p[t[1]], c1)   # c1 = x_a & x_b
        qc.ccx(c1, p[t[2]], c0_step := c0) if False else None
        qc.ccx(c1, p[t[2]], c0)        # attempt to set c0 (XOR semantics)
        qc.ccx(p[t[0]], p[t[1]], c1)   # uncompute c1

    # NOTE: the above XORs c0 with each triple term. For weight==4 all four terms=1 -> XOR=0 (wrong).
    # Fix weight==4 case: add its correction (x0&x1&x2&x3 toggles c0 back to 1).
    qc.mcx([x0, x1, x2, x3], c0)       # now c0 = 1 for weight 3 and weight 4 -> c0 = (weight>=3)
    qc.x(c0)                           # c0 = 1 iff weight<=2  == w-ok

    # ---- combine: mark iff all 5 edge flags AND weight-ok ----
    controls = edge_anc + [c0]
    qc.h(w)
    qc.mcx(controls, w)                # phase kickback target
    qc.h(w)

    # ---- uncompute weight logic (mirror) ----
    qc.x(c0)
    qc.mcx([x0, x1, x2, x3], c0)
    for t in reversed(triples):
        qc.ccx(p[t[0]], p[t[1]], c1)
        qc.ccx(c1, p[t[2]], c0)
        qc.ccx(p[t[0]], p[t[1]], c1)

    # ---- uncompute edge flags (mirror) ----
    for (u, v), a in zip(reversed(edges), reversed(edge_anc)):
        qc.x(a)
        qc.x(p[u])
        qc.x(p[v])
        qc.ccx(p[u], p[v], a)
        qc.x(p[u])
        qc.x(p[v])
