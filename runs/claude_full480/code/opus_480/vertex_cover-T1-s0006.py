from qiskit import QuantumCircuit
from math import pi


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    v0, v1, v2, v3 = (problem_qubits[0], problem_qubits[1],
                      problem_qubits[2], problem_qubits[3])
    edges = [(0, 1), (0, 3), (1, 2), (1, 3), (2, 3)]

    edge_anc = ancilla_qubits[0:5]   # one ancilla per edge (OR of endpoints)
    cnt_anc = ancilla_qubits[5:8]    # 3-bit popcount register (values 0..4)
    result = None  # not used; we phase on a combined flag via mcx into edges? use direct

    # ---- compute: each edge ancilla = OR(endpoint_a, endpoint_b) ----
    def edge_or(i, a, b):
        anc = edge_anc[i]
        qc.x(problem_qubits[a])
        qc.x(problem_qubits[b])
        qc.x(anc)
        qc.ccx(problem_qubits[a], problem_qubits[b], anc)  # anc = 1 - (~a & ~b) = a OR b
        qc.x(problem_qubits[a])
        qc.x(problem_qubits[b])

    for i, (a, b) in enumerate(edges):
        edge_or(i, a, b)

    # ---- compute: popcount of the 4 problem bits into 3-bit register cnt_anc ----
    # cnt_anc[0]=bit0, cnt_anc[1]=bit1, cnt_anc[2]=bit2 of (x0+x1+x2+x3)
    c0, c1, c2 = cnt_anc[0], cnt_anc[1], cnt_anc[2]

    def add_one(src):
        # add the single-bit src into the counter (ripple), counter max reaches 4
        qc.ccx(src, c1, c2)   # carry into c2 when c1 already set and adding produces carry through c0
        qc.ccx(src, c0, c1)   # carry from bit0 to bit1
        qc.cx(src, c0)        # add into bit0

    for src in (v0, v1, v2, v3):
        add_one(src)

    # size <= 2  means bit2 == 0 AND NOT(bit1==1 AND bit0==1)  i.e. count in {0,1,2}
    # count<=2 : c2==0 and not(c1==1 and c0==1)
    # We want flag = (all edges covered) AND (count <= 2).
    # all edges covered: all edge_anc == 1.
    # count<=2 condition qubit: build into result ancilla? we reused all 8 ancillas.
    # Instead phase directly with a single multi-controlled Z conditioned on the
    # full predicate expressed over edge_anc and the counter.
    #
    # count<=2  <=>  c2==0 and (c0 NAND c1).
    # Enumerate the two accepted count-patterns among (c2,c1,c0): 000,001,010.
    # These are exactly: c2==0 AND NOT(c1 AND c0).
    #
    # We realize the phase as: for the accepted region, all edge_anc==1.
    # Use a single MCP(pi) controlled on {all edge_anc ==1, c2==0, and (c1 AND c0)==0}.
    # Decompose "c2==0 and not(c1&c0)" = (c2==0 and c1==0) OR (c2==0 and c0==0).
    # These two subsets are disjoint? 000/001 (c1==0) and 000/010 (c0==0) overlap at 000.
    # To avoid double phase, use inclusion-exclusion:
    #   phase A: c2==0,c1==0 (counts 000,001)  -> covers count 0,1
    #   phase B: c2==0,c0==0,c1==1 (count 010) -> count 2
    # disjoint. Apply MCZ over edges + these counter controls for each.

    # controls: 5 edge ancillas must be 1; counter conditions vary.
    # subset A: c1==0,c2==0  (open c0)
    qc.x(c1); qc.x(c2)
    qc.mcp(pi, edge_anc + [c1, c2], v0)  # need a target; use borrowed phase kickback:
    qc.x(c1); qc.x(c2)

    # The above mcp uses v0 as target which is wrong (it's a control-of-phase target,
    # but mcp applies phase on |11..1> of controls+target). To phase the state itself
    # we instead put phase on the full control set including a fixed-|1> ancilla.
    # Simpler: use mcp on all-but-one control with the last as target — phase applies
    # only when ALL listed qubits are 1, which is exactly our predicate region.
    # Redo cleanly below (the two lines above are neutralized by re-applying inverse):
    qc.x(c1); qc.x(c2)
    qc.mcp(-pi, edge_anc + [c1, c2], v0)
    qc.x(c1); qc.x(c2)

    # ---- clean phase application ----
    # subset A: edges all 1, c1==0, c2==0
    qc.x(c1); qc.x(c2)
    qc.mcp(pi, edge_anc + [c2, v0], c1) if False else None
    qc.x(c1); qc.x(c2)

    # Proper: treat the whole set {edge_anc..., plus counter-condition qubits} as
    # controls of a single mcp on one of them acting as target; phase(pi) fires iff
    # every listed qubit is |1>. Map each accepted region to an all-ones pattern by
    # X-flipping the zero-required qubits.

    # Region A (counts 0,1): require e0..e4==1, c1==0, c2==0
    qc.x(c1); qc.x(c2)
    ctrlsA = edge_anc[:-1] + [c1, c2]
    qc.mcp(pi, ctrlsA, edge_anc[-1])
    qc.x(c1); qc.x(c2)

    # Region B (count 2): require e0..e4==1, c0==0, c1==1, c2==0
    qc.x(c0); qc.x(c2)
    ctrlsB = edge_anc[:-1] + [c0, c1, c2]
    qc.mcp(pi, ctrlsB, edge_anc[-1])
    qc.x(c0); qc.x(c2)

    # ---- uncompute popcount (mirror) ----
    def add_one_inv(src):
        qc.cx(src, c0)
        qc.ccx(src, c0, c1)
        qc.ccx(src, c1, c2)

    for src in (v3, v2, v1, v0):
        add_one_inv(src)

    # ---- uncompute edge ancillas (mirror) ----
    def edge_or_inv(i, a, b):
        anc = edge_anc[i]
        qc.x(problem_qubits[a])
        qc.x(problem_qubits[b])
        qc.ccx(problem_qubits[a], problem_qubits[b], anc)
        qc.x(anc)
        qc.x(problem_qubits[a])
        qc.x(problem_qubits[b])

    for i, (a, b) in reversed(list(enumerate(edges))):
        edge_or_inv(i, a, b)
