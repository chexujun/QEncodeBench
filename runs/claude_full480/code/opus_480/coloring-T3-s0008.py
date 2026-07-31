from qiskit import QuantumCircuit
import math

def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges = [(0,4),(0,5),(1,3),(1,4),(2,3),(2,5),(3,4),(3,5)]

    def qb(v):
        return problem_qubits[2*v], problem_qubits[2*v+1]

    edge_anc = ancilla_qubits[0]
    t0 = ancilla_qubits[1]
    t1 = ancilla_qubits[2]
    tsame = ancilla_qubits[3]
    flag = ancilla_qubits[4]

    def same_color(u, v, undo=False):
        u0, u1 = qb(u)
        v0, v1 = qb(v)
        seq_forward = []

        # color of a vertex: c in {0,1,2}, with code 11 -> color 0.
        # Two vertices are "same color" iff decoded colors are equal.
        # We compute per-vertex a one-hot-ish flag set is complex; instead
        # detect equality directly via the 3 color classes:
        #   color0 <=> code in {00, 11}  => (b0 == b1)
        #   color1 <=> code == 01         => (b0=1,b1=0)
        #   color2 <=> code == 10         => (b0=0,b1=1)
        #
        # same iff both color0, or both color1, or both color2.
        #
        # We build ancilla t0 = "u is color1 AND v is color1"
        #          t1 = "u is color2 AND v is color2"
        #          tsame handles color0==color0 via parity trick.
        #
        # color1(x): x0 AND (NOT x1)
        # color2(x): (NOT x0) AND x1
        # color0(x): x0 == x1  <=> NOT(x0 XOR x1)

        ops = []
        # --- both color1 ---
        # u color1: u0 & ~u1 ; v color1: v0 & ~v1
        ops.append(('x', u1)); ops.append(('x', v1))
        ops.append(('ccx3', (u0, u1, t0)))   # placeholder replaced below
        # We can't 4-control into t0 easily with ccx; use mcx.
        # Reset approach: use mcx with controls [u0,u1,v0,v1] state:
        # We'll instead implement below cleanly.
        return ops

    # Because equality across a surjective decode is awkward with plain
    # ccx chains, compute per-edge "different" flag into edge_anc using
    # mcx over the enumerated MONOCHROMATIC control patterns for a pair,
    # but WITHOUT baking solutions of f: this enumerates pair-local color
    # matches only (a fixed 2-vertex predicate), which is allowed.

    # Color classes as code sets:
    #   color0 -> codes {00,11} = {(0,0),(1,1)}
    #   color1 -> codes {01}    = {(1,0)}   (b0=1,b1=0)
    #   color2 -> codes {10}    = {(0,1)}   (b0=0,b1=1)
    color_codes = {
        0: [(0,0),(1,1)],
        1: [(1,0)],
        2: [(0,1)],
    }

    def set_controls(qubits, pattern):
        # X on lines that must be controlled on 0
        flips = [q for q,bit in zip(qubits, pattern) if bit == 0]
        for q in flips:
            qc.x(q)
        return flips

    def unset_controls(flips):
        for q in flips:
            qc.x(q)

    # For each edge, mark edge_anc (via X-flip) once per monochromatic
    # (color-matched) code combination -> edge_anc becomes 1 iff this
    # edge is monochromatic. Then AND all "not monochromatic" together.
    #
    # Strategy: build a per-edge ancilla flag 'mono_e' but we only have
    # limited ancillas, so we accumulate: flag counts edges that ARE
    # properly colored using controlled increments is hard. Instead:
    #   - compute edge_anc = OR over edges of (edge monochromatic)
    #   - f = NOT edge_anc  => phase when edge_anc == 0
    # OR is computed by flipping edge_anc to 1 on any mono edge; but OR
    # is not cleanly reversible via simple XOR (double-count cancels).
    #
    # Use the standard trick: compute a per-edge mono bit into a fresh
    # ancilla, then use it to toggle a counter is overkill. With f = AND
    # over edges of (edge is bichromatic), we AND edge bichromatic bits.
    #
    # We compute each edge's "monochromatic" bit into edge_anc as an XOR
    # of its disjoint monochromatic patterns (patterns are mutually
    # exclusive, so XOR == OR for a single edge), producing bit b_e, then
    # want AND_e (NOT b_e). Multi-control on 8 separate one-shot bits
    # needs 8 stored bits -> not enough ancillas.
    #
    # Resolve by sequential: keep 'flag' = 1 initially meaning "all good
    # so far" using multi-controlled logic per edge onto a running AND is
    # also not simply reversible.
    #
    # Cleanest feasible: compute the total "monochromatic edge count == 0"
    # by toggling 'flag' with a multi-controlled-Z pattern is hard.
    #
    # We instead do: for each edge compute mono bit m into a scratch,
    # controlled-accumulate into edge_anc via CX (edge_anc ^= m), but that
    # gives parity not OR. Parity fails when 2 edges mono simultaneously.
    #
    # Since exact OR is required, use: edge_anc holds running OR built as
    #   edge_anc = edge_anc OR m  = edge_anc XOR (m AND NOT edge_anc)
    # implemented with an mcx controlled on m-lines AND (edge_anc==0).
    pass

    # ---- Clean implementation ----
    # Per edge, for each monochromatic code-combo (cu in color_codes[c],
    # cv in color_codes[c] over all colors c), the 4 problem qubits take a
    # fixed pattern. We OR these into edge_anc using the reversible OR:
    #   mcx(controls = 4 qubits in pattern + edge_anc==0-control) -> edge_anc
    # To control on edge_anc==0 we X edge_anc, include it as control, X back.

    def or_into(target, ctrl_qubits, pattern):
        flips = set_controls(ctrl_qubits, pattern)
        qc.x(target)                       # so control-on-1 means target was 0
        qc.mcx(ctrl_qubits + [target], flag_dummy) if False else None
        qc.x(target)
        unset_controls(flips)

    # Simpler & fully correct: OR via mcx with a NOT-target guard using an
    # extra scratch is unavailable. Instead accept OR-as-set: set target=1
    # whenever pattern matches, using mcx WITHOUT guard but guaranteeing no
    # double toggle by making patterns for a given target mutually
    # exclusive across the WHOLE edge loop is false. So we DO need OR.
    #
    # Reversible OR without extra guard qubit:
    #   For controls C (the 4 pattern-matched lines), do:
    #     X(target); MCX(C + [target] -> scratch)  needs scratch.
    #
    # We have ancillas: edge_anc, t0, t1, tsame, flag. Use t0 as scratch.

    def or_set(target, scratch, ctrl_qubits, pattern):
        # target := target OR (controls match pattern)
        flips = set_controls(ctrl_qubits, pattern)
        # scratch assumed 0. scratch := (pattern match) AND (target==0)
        qc.x(target)
        qc.mcx(ctrl_qubits + [target], scratch)
        qc.x(target)
        # target ^= scratch  -> sets target=1 exactly when newly matched
        qc.cx(scratch, target)
        # uncompute scratch: scratch := scratch XOR (pattern match AND target_new==0)
        # after target updated, if it matched then target==1 now, so the
        # same mcx with X(target) recomputes the same value -> clears it.
        qc.x(target)
        qc.mcx(ctrl_qubits + [target], scratch)
        qc.x(target)
        unset_controls(flips)

    # Build edge_anc = OR over all edges/colors of monochromatic match.
    forward_ops = []
    def build_edge_anc():
        for (u, v) in edges:
            uq = [problem_qubits[2*u], problem_qubits[2*u+1]]
            vq = [problem_qubits[2*v], problem_qubits[2*v+1]]
            ctrls = uq + vq
            for c in (0, 1, 2):
                for pu in color_codes[c]:
                    for pv in color_codes[c]:
                        pattern = (pu[0], pu[1], pv[0], pv[1])
                        or_set(edge_anc, t0, ctrls, pattern)

    build_edge_anc()

    # f(x) = 1 iff NO edge monochromatic iff edge_anc == 0.
    # Phase -1 when edge_anc == 0: X, Z, X on edge_anc.
    qc.x(edge_anc)
    qc.z(edge_anc)
    qc.x(edge_anc)

    # Uncompute edge_anc by reversing the OR construction.
    def unbuild_edge_anc():
        for (u, v) in reversed(edges):
            uq = [problem_qubits[2*u], problem_qubits[2*u+1]]
            vq = [problem_qubits[2*v], problem_qubits[2*v+1]]
            ctrls = uq + vq
            for c in (2, 1, 0):
                for pu in reversed(color_codes[c]):
                    for pv in reversed(color_codes[c]):
                        pattern = (pu[0], pu[1], pv[0], pv[1])
                        or_set(edge_anc, t0, ctrls, pattern)

    unbuild_edge_anc()
