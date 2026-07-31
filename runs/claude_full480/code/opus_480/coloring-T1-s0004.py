from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 2), (1, 3), (2, 3)]

    def vq(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # For each edge we compute an ancilla = 1 iff the two endpoints have the
    # SAME color (edge violated). We need the predicate f = AND over edges of
    # (colors differ) = NOT (any edge same). We compute per-edge "same" flags
    # into 3 ancillas, and then phase-flip only when ALL edges are "different",
    # i.e. all three same-flags are 0. That is an MCP with all-zero controls.
    #
    # Color equality with the surjective decode (11 -> color 0):
    # colors of vertices u,v are equal iff codes map to same color.
    # color(c): 0->0,1->1,2->2,3->0. So color equal iff:
    #   (cu==cv) OR ({cu,cv} subset {0,3} i.e. both decode to 0).
    # Both-decode-to-0 means cu in {00,11} and cv in {00,11}.
    #
    # Let for a vertex: define helper booleans on its 2 code bits (b0,b1):
    #   is0  = (b0=0,b1=0)   code 00
    #   is1  = (b0=1,b1=0)   code 01
    #   is2  = (b0=0,b1=1)   code 10
    #   is3  = (b0=1,b1=1)   code 11
    # color0 = is0 OR is3 ; color1 = is1 ; color2 = is2.
    #
    # Edge "same color" =
    #   (color0_u AND color0_v) OR (is1_u AND is1_v) OR (is2_u AND is2_v).
    #
    # We compute this per-edge into one ancilla using compute->...; but we need
    # the flag as a clean boolean. We build it via the three disjoint AND terms
    # (they are mutually exclusive), XOR-ing them into the edge ancilla; since
    # terms are mutually exclusive, XOR == OR.

    # We'll need scratch ancillas. We have exactly 4 ancillas and 3 edges.
    # Strategy: process edges sequentially, but we must keep all 3 edge flags
    # simultaneously to do the joint all-zero MCP. That uses 3 ancillas for the
    # flags + 1 scratch ancilla for intermediate AND terms. Total 4. Good.

    edge_flag = [ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]]
    scratch = ancilla_qubits[3]

    def compute_edge_same(u, v, flag, uncompute=False):
        b0u, b1u = vq(u)
        b0v, b1v = vq(v)

        # Term A: color0_u AND color0_v, where color0 = (b0,b1)!=... actually
        # color0 = is0 OR is3 = (b1==b0)  because 00 ->true, 11 ->true,
        # 01->false,10->false. Indeed color0 iff b0==b1.
        # color1 = is1 = b0 AND (NOT b1).
        # color2 = is2 = b1 AND (NOT b0).
        #
        # color0_u = (b0u == b1u). Compute into a temp bit t_u using scratch:
        # We'll compute each AND term into scratch, XOR into flag, uncompute.

        ops = []

        # --- Term A: color0_u AND color0_v ---
        # color0 = NOT(b0 XOR b1). We compute p_u = b0u XOR b1u (0 means color0),
        # p_v = b0v XOR b1v. color0_u AND color0_v = (p_u==0)AND(p_v==0)
        # = NOT p_u AND NOT p_v. Use ccx with both controls negated.
        # Compute p into b0 register? We must not disturb problem qubits, so
        # compute p onto scratch requires two bits. Instead: color0_u AND
        # color0_v true iff b0u==b1u AND b0v==b1v. We implement using scratch
        # by an mcx with control-state pattern? mcx has no negation. So we X
        # the relevant qubits to convert zero-conditions, apply mcx, then X back.
        #
        # color0_u AND color0_v is NOT a simple product of single qubits;
        # it's over 4 qubits with equality constraints. Enumerate the allowed
        # (b0u,b1u,b0v,b1v): b0u==b1u and b0v==b1v ->
        #   (0,0,0,0),(0,0,1,1),(1,1,0,0),(1,1,1,1).
        # That's 4 basis combos -> 4 mcx terms with negated controls.
        for (a0, a1, c0, c1) in [(0, 0, 0, 0), (0, 0, 1, 1),
                                 (1, 1, 0, 0), (1, 1, 1, 1)]:
            ops.append(('mcx4', (b0u, a0), (b1u, a1), (b0v, c0), (b1v, c1)))

        # --- Term B: is1_u AND is1_v --- code 01 means b0=1,b1=0
        ops.append(('mcx4', (b0u, 1), (b1u, 0), (b0v, 1), (b1v, 0)))

        # --- Term C: is2_u AND is2_v --- code 10 means b0=0,b1=1
        ops.append(('mcx4', (b0u, 0), (b1u, 1), (b0v, 0), (b1v, 1)))

        # These terms are mutually exclusive, so XOR-ing each directly into flag
        # yields the OR. Each term is a 4-control Toffoli with control states.
        seq = ops if not uncompute else list(reversed(ops))
        for op in seq:
            _, (q0, s0), (q1, s1), (q2, s2), (q3, s3) = op
            controls = [q0, q1, q2, q3]
            states = [s0, s1, s2, s3]
            for q, s in zip(controls, states):
                if s == 0:
                    qc.x(q)
            qc.mcx(controls, flag)
            for q, s in zip(controls, states):
                if s == 0:
                    qc.x(q)

    # Compute all three edge flags.
    for i, (u, v) in enumerate(edges):
        compute_edge_same(u, v, edge_flag[i])

    # Phase flip iff all edge flags == 0 (all edges have differing colors).
    # Multi-controlled Z with all controls in state 0: X all, mcp(pi), X all.
    for f in edge_flag:
        qc.x(f)
    qc.h(edge_flag[-1])
    qc.mcx(edge_flag[:-1], edge_flag[-1])
    qc.h(edge_flag[-1])
    for f in edge_flag:
        qc.x(f)

    # Uncompute all three edge flags (mirror).
    for i, (u, v) in reversed(list(enumerate(edges))):
        compute_edge_same(u, v, edge_flag[i], uncompute=True)
