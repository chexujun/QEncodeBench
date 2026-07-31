import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 2), (2, 3)]

    def vqubits(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # For an edge (u, w): colors differ unless decode(u) == decode(w).
    # Codes: 00->0, 01->1, 10->2, 11->0.  So decode == 0 for codes 00 or 11.
    # Two vertices share a color iff:
    #   both decode to 0: (u in {00,11}) and (w in {00,11})
    #   both are 01
    #   both are 10
    # We compute per-edge a "same-color" flag into an edge ancilla, OR them
    # (via marking) — but easier: predicate f = AND over edges of (colors differ)
    # = NOT (OR over edges of same-color).  We compute e_i = same-color(edge i)
    # into ancilla, then f = 1 iff all e_i == 0.
    #
    # We have 3 edges and 4 ancillas: use ancillas[0..2] as per-edge same-color
    # flags, ancilla[3] as scratch.

    edge_anc = ancilla_qubits[:3]
    scratch = ancilla_qubits[3]

    def code_is_zero_color(v, target, on):
        # Set 'target' toggled when vertex v decodes to color 0 (code 00 or 11),
        # using scratch-free approach: decode0 = (b0==b1). b0 XOR b1 == 0.
        # We compute p = b0 XOR b1 into 'on', then target ^= NOT p handled by caller.
        pass

    def compute_same_color(v_u, v_w, out):
        u0, u1 = vqubits(v_u)
        w0, w1 = vqubits(v_w)
        # same color cases -> set 'out' = 1 if colors equal.
        # Use scratch to hold intermediate; ensure clean.
        # Case A: both decode color 0: (u0==u1) AND (w0==w1).
        #   pu0 = (u0 XOR u1)==0 ; pw0 = (w0 XOR w1)==0
        # Case B: both 01: u0=1,u1=0,w0=1,w1=0
        # Case C: both 10: u0=0,u1=1,w0=0,w1=1
        #
        # equal-color <=> decode(u)==decode(w).  Enumerate via mcx per case,
        # toggling 'out'.  These cases are mutually exclusive, so parity == OR.

        # Case A: both color 0.  decode0(v): code 00 or 11 -> b0 == b1.
        # Build with scratch: we need AND of (u0==u1) and (w0==w1).
        # Represent (u0==u1): X on u0,u1 controls... use: after cx u1->u0? Avoid
        # mixing problem qubits. Instead map equality to controls via ancilla scratch.
        #
        # su = u0 XOR u1 (0 means equal). compute into scratch.
        qc.cx(u0, scratch)
        qc.cx(u1, scratch)  # scratch = u0 XOR u1
        # sw into 'out' temporarily? need both zero simultaneously. Use out to
        # hold w equality, then combine.
        qc.cx(w0, out)
        qc.cx(w1, out)  # out = w0 XOR w1
        # both-color-0 flag = (scratch==0) AND (out==0). We toggle into... need a
        # place. Reuse: apply X to scratch,out so 1 means equal, ccx onto a temp.
        # But we only have scratch+out here for this edge. We'll accumulate the
        # three-case parity directly on 'out' at the end, so restructure:
        # First undo out; better handle full logic below.
        qc.cx(w1, out)
        qc.cx(w0, out)  # out back to original
        qc.cx(u1, scratch)
        qc.cx(u0, scratch)  # scratch back to 0

        # Direct enumeration approach (clean): toggle 'out' for each equal-color
        # combination of (code_u, code_w). Equal-color combos:
        #   colors both 0: code_u in {00,11}, code_w in {00,11} -> 4 combos
        #   both 1: (01,01)
        #   both 2: (10,10)
        combos = []
        zero_codes = [(0, 0), (1, 1)]  # (b0,b1)
        for cu in zero_codes:
            for cw in zero_codes:
                combos.append((cu, cw))
        combos.append(((1, 0), (1, 0)))  # color 1 = code 01
        combos.append(((0, 1), (0, 1)))  # color 2 = code 10
        for (ub0, ub1), (wb0, wb1) in combos:
            ctrls = [u0, u1, w0, w1]
            pat = [ub0, ub1, wb0, wb1]
            for q, bit in zip(ctrls, pat):
                if bit == 0:
                    qc.x(q)
            qc.mcx(ctrls, out)
            for q, bit in zip(ctrls, pat):
                if bit == 0:
                    qc.x(q)

    def uncompute_same_color(v_u, v_w, out):
        compute_same_color(v_u, v_w, out)  # self-inverse (mcx pairs), toggles back

    # Compute each edge same-color flag.
    for i, (u, w) in enumerate(edges):
        compute_same_color(u, w, edge_anc[i])

    # f = 1 iff all edge flags == 0.  Phase -1 on that state:
    # apply X to each edge flag, mcp(pi) controlled by all three -> phase when all
    # were 0; then X back.
    for a in edge_anc:
        qc.x(a)
    qc.h(edge_anc[2])
    qc.mcx(edge_anc[:2], edge_anc[2])
    qc.h(edge_anc[2])
    for a in edge_anc:
        qc.x(a)

    # Uncompute edge flags.
    for i, (u, w) in enumerate(edges):
        uncompute_same_color(u, w, edge_anc[i])
