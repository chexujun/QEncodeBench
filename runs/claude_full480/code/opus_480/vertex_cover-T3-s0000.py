from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0,1),(0,4),(1,2),(1,3),(1,4),(1,5),(2,5),(3,4)]
    p = problem_qubits
    edge_anc = ancilla_qubits[0:8]        # OR of each edge's endpoints
    c0, c1, c2 = ancilla_qubits[8], ancilla_qubits[9], ancilla_qubits[10]

    # ---- compute edge coverage: edge_anc[j] = x_a OR x_b ----
    def edge_or(a, b, anc):
        qc.x(p[a]); qc.x(p[b])
        qc.x(anc)
        qc.ccx(p[a], p[b], anc)      # anc = a OR b
        qc.x(p[b]); qc.x(p[a])

    for j, (a, b) in enumerate(edges):
        edge_or(a, b, edge_anc[j])

    # ---- popcount of 6 problem bits into (c2 c1 c0) via controlled increment ----
    def inc(ctrl):
        qc.mcx([ctrl, c0, c1], c2)
        qc.ccx(ctrl, c0, c1)
        qc.cx(ctrl, c0)
    for i in range(6):
        inc(p[i])

    # count value in 0..6. count > 4 (invalid) iff c2==1 AND (c1==1 OR c0==1):
    #   5 = 101, 6 = 110  (7 impossible). Valid (<=4) iff NOT(c2 AND (c1 OR c0)).
    #
    # Phase target: -1 iff (all 8 edges covered) AND (count valid).
    #   = -1 on {all edges} MINUS the invalid-count subset of {all edges}.
    # Apply pi on {all edges}; then apply pi again on {all edges AND count-invalid}
    # to flip those specific states back (pi+pi = 2pi = identity phase).

    controls_edges = edge_anc[:]                      # all 8 edge ancillas == 1

    # Phase A: -1 on every state with all edges covered (target last control via mcp)
    qc.mcp(math.pi, controls_edges[:-1], controls_edges[-1])

    # count-invalid = c2 AND (c1 OR c0), split into two disjoint covers:
    #   term1: c2 AND c1                 -> covers 110 (=6) and 111(n/a)
    #   term2: c2 AND c0 AND (NOT c1)    -> covers 101 (=5)
    # Phase B1: +flip on all edges AND c2 AND c1
    qc.mcp(math.pi, controls_edges + [c1], c2)
    # Phase B2: +flip on all edges AND c2 AND c0 AND (NOT c1)
    qc.x(c1)
    qc.mcp(math.pi, controls_edges + [c0, c1], c2)
    qc.x(c1)

    # ---- uncompute popcount (reverse increments) ----
    def inc_inv(ctrl):
        qc.cx(ctrl, c0)
        qc.ccx(ctrl, c0, c1)
        qc.mcx([ctrl, c0, c1], c2)
    for i in reversed(range(6)):
        inc_inv(p[i])

    # ---- uncompute edge coverage ----
    def edge_or_inv(a, b, anc):
        qc.x(p[a]); qc.x(p[b])
        qc.ccx(p[a], p[b], anc)
        qc.x(anc)
        qc.x(p[b]); qc.x(p[a])
    for j, (a, b) in reversed(list(enumerate(edges))):
        edge_or_inv(a, b, edge_anc[j])
