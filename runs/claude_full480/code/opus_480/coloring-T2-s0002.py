import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 2), (0, 3), (1, 2), (2, 3)]

    # Per-vertex qubits: vertex v -> (low, high)
    def vq(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # We need: for each edge, decoded colors differ.
    # Decode: c in {0,1,2,3}; color(c) = c except color(3)=0.
    # So color(a)==color(b) iff:
    #   (a==b) with a,b in {0,1,2}, OR one is 0 and other is 3, OR both 3, OR
    # Precisely: colors equal iff decode(a)==decode(b).
    # decode: 00->0, 01->1, 10->2, 11->0.
    # color==0 set = {00,11}; color1={01}; color2={10}.
    #
    # Edge is "good" (differ) iff NOT same color.
    # f(x)=1 iff ALL edges good.
    #
    # Strategy: for each edge compute an ancilla bit "bad_e" = 1 if same color.
    # Then f = AND over edges of (NOT bad_e) = 1 iff all bad_e == 0.
    # Multi-controlled phase on all bad_e being 0: wrap with X.
    #
    # We have 6 ancillas, 5 edges -> use 5 ancillas for edge-bad flags,
    # 1 spare available if needed.
    #
    # Compute bad_e for edge (u,v): same color.
    # Let u=(u0,u1), v=(v0,v1). colors:
    #   colorclass depends on (b0,b1): class0={(0,0),(1,1)}, class1={(0,1)}, class2={(1,0)}.
    # same color iff class(u)==class(v).
    #
    # Define for a vertex two indicator conditions on its 2 bits:
    #   is1 = (b0=1,b1=0)  -> color1
    #   is2 = (b0=0,b1=1)  -> color2
    #   is0 = (b0=b1)      -> color0  (00 or 11)
    #
    # same color iff (is0_u & is0_v) | (is1_u & is1_v) | (is2_u & is2_v).
    #
    # Compute bad_e into ancilla by adding (XOR) the three product terms.
    # These three products are mutually exclusive per fixed assignment? For a
    # fixed x each vertex is in exactly one class, so at most one product term
    # is 1; XOR-accumulation == OR here. Good, reversible via mirror.

    edge_anc = ancilla_qubits[:len(edges)]

    def compute_bad(u, v, anc):
        u0, u1 = vq(u)
        v0, v1 = vq(v)
        # term is0_u & is0_v : is0 = (b0==b1) = NOT(b0 xor b1)
        # Rather than a fresh ancilla per subterm, build each product with a
        # multi-controlled X onto anc, using X-conjugation to encode bit values.
        # is0 means b0==b1. Represent condition "b0==b1" for a vertex is a
        # 2-bit equality; controlling on it directly isn't a single pattern.
        # Split class0 into its two codes 00 and 11 explicitly:
        # same-color contributions (exclusive patterns on 4 bits u0u1v0v1):
        #   color0-color0: u in {00,11}, v in {00,11} -> 4 combos
        #   color1-color1: u=10? note color1 code=01 => (b0=1,b1=0)? careful:
        #     color1 = c=1 = 01 binary = b0=1,b1=0. So (u0=1,u1=0),(v0=1,v1=0)
        #   color2-color2: c=2 =10 => b0=0,b1=1. (u0=0,u1=1),(v0=0,v1=1)
        # Enumerate exact 4-bit patterns (u0,u1,v0,v1) that are same-color:
        patterns = []
        # color0 codes for a vertex: (b0,b1) in {(0,0),(1,1)}
        c0 = [(0, 0), (1, 1)]
        c1 = [(1, 0)]
        c2 = [(0, 1)]
        for cls in (c0, c1, c2):
            for (a0, a1) in cls:
                for (b0, b1) in cls:
                    patterns.append((a0, a1, b0, b1))
        ctrls = [u0, u1, v0, v1]
        for pat in patterns:
            # X-conjugate zeros so mcx triggers on this exact pattern
            zeros = [ctrls[i] for i in range(4) if pat[i] == 0]
            for z in zeros:
                qc.x(z)
            qc.mcx(ctrls, anc)
            for z in zeros:
                qc.x(z)

    # Compute all edge-bad flags
    for (u, v), anc in zip(edges, edge_anc):
        compute_bad(u, v, anc)

    # Phase: -1 iff all bad flags are 0 (all edges good).
    # Flip all bad flags, multi-controlled-Z, flip back.
    for anc in edge_anc:
        qc.x(anc)
    # multi-controlled Z on the edge_anc qubits: use last as target with H trick
    if len(edge_anc) == 1:
        qc.z(edge_anc[0])
    else:
        ctrls = edge_anc[:-1]
        tgt = edge_anc[-1]
        qc.h(tgt)
        qc.mcx(ctrls, tgt)
        qc.h(tgt)
    for anc in edge_anc:
        qc.x(anc)

    # Uncompute all edge-bad flags (mirror, reverse order)
    for (u, v), anc in zip(reversed(edges), reversed(edge_anc)):
        compute_bad(u, v, anc)
