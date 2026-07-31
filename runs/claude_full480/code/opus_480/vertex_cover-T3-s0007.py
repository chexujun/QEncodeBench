from qiskit import QuantumCircuit
from math import pi


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 4), (0, 5), (1, 3), (2, 3), (2, 4), (3, 4), (4, 5)]

    v = [problem_qubits[i] for i in range(6)]
    # ancillas
    edge_anc = ancilla_qubits[0:7]      # one per edge (edge covered flag)
    all_edges = ancilla_qubits[7]       # AND of all edge flags
    cnt = ancilla_qubits[8:10] + [ancilla_qubits[7]]  # placeholder, redefine below

    # We need a clean set of ancillas. Use:
    #   edge_anc[0..6] : 7 edge-covered flags
    #   c0, c1, c2     : 3 count-bit qubits (popcount of x, max value 6 -> 3 bits)
    # Total ancillas needed = 7 + 3 = 10. Good.
    c0 = ancilla_qubits[7]
    c1 = ancilla_qubits[8]
    c2 = ancilla_qubits[9]

    # ---------- COMPUTE ----------
    # 1) Edge covered flags: edge (a,b) covered iff v_a OR v_b.
    #    OR(a,b) = NOT( NOT a AND NOT b ). Compute into edge_anc[i]:
    #    set edge_anc = 1, then if both endpoints are 0 -> set to 0.
    for i, (a, b) in enumerate(edges):
        e = edge_anc[i]
        qc.x(e)                     # e = 1
        qc.x(v[a]); qc.x(v[b])
        qc.ccx(v[a], v[b], e)       # if !a & !b then flip e -> 0
        qc.x(v[a]); qc.x(v[b])
    # now edge_anc[i] = 1 iff edge i covered.

    # 2) Popcount of the 6 vertex bits into (c2 c1 c0), a 3-bit ripple counter.
    #    Add each vertex bit into the counter.
    for i in range(6):
        b = v[i]
        # carry from c1 to c2 when adding: c2 ^= b & c0 & c1
        qc.mcx([b, c0, c1], c2)
        # carry from c0 to c1: c1 ^= b & c0
        qc.ccx(b, c0, c1)
        # add into c0: c0 ^= b
        qc.cx(b, c0)

    # 3) Size <= 3 predicate. count in (c2 c1 c0), value 0..6.
    #    count <= 3 means NOT(count >= 4). count >= 4 iff c2==1 and (c1 or c0),
    #    i.e. values 4,5,6 -> (c2,c1,c0) = 100,101,110. value 4 =100 (>=4),
    #    so count>=4 iff c2==1. (4=100,5=101,6=110 all have c2=1; 0..3 have c2=0)
    #    Therefore size<=3 iff c2==0.

    # ---------- PHASE ----------
    # Marked iff (all edges covered) AND (c2 == 0).
    # all edges covered = AND of edge_anc[0..6]; combined control including !c2.
    qc.x(c2)  # now c2==1 means size<=3
    ctrls = list(edge_anc) + [c2]
    qc.h(all_edges) if False else None
    # Apply multi-controlled Z (phase -1) with all edge flags and c2 as controls.
    qc.mcp(pi, ctrls[:-1], ctrls[-1])
    qc.x(c2)  # restore

    # ---------- UNCOMPUTE ----------
    for i in reversed(range(6)):
        b = v[i]
        qc.cx(b, c0)
        qc.ccx(b, c0, c1)
        qc.mcx([b, c0, c1], c2)

    for i, (a, b) in enumerate(edges):
        e = edge_anc[i]
        qc.x(v[a]); qc.x(v[b])
        qc.ccx(v[a], v[b], e)
        qc.x(v[a]); qc.x(v[b])
        qc.x(e)
