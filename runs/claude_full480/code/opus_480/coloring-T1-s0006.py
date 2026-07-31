import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Vertex v uses code bits: b0 = problem_qubits[2v], b1 = problem_qubits[2v+1]
    # Colors (surjective): 00->0, 01->1, 10->2, 11->0.
    # Two vertices share a color iff their codes are "equal-as-colors".
    # Enumerate the color-equality pairs of codes:
    #   color0 codes: {00, 11}; color1: {01}; color2: {10}
    # For an edge (u,w) let cu,cw be codes. They are monochromatic iff:
    #   (cu==cw) OR (cu,cw in {00,11} in some order i.e. one is 00 and other 11).
    # We build a per-edge ancilla flag = 1 iff edge is monochromatic (bad),
    # then f = AND over edges of (NOT bad) = 1 iff no edge is bad.

    edges = [(0, 2), (1, 2), (2, 3)]

    def vb(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # For each edge we need ancilla flag "mono". We only have 4 ancillas and
    # 3 edges -> use ancillas[0..2] for edge flags, ancilla[3] as scratch.
    edge_flags = [ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]]
    scratch = ancilla_qubits[3]

    # Helper: compute mono flag for an edge into target ancilla `flag`,
    # using `scratch` (must be |0> in and out).
    # Codes u=(u0,u1), w=(w0,w1). Define color-equality predicate:
    #   mono = 1 iff colors equal.
    # Color(c): c in {00,11} -> 0 ; 01 -> 1 ; 10 -> 2.
    # Let's define color-class membership signals via basis matching.
    # Enumerate monochromatic code-pairs (u,w) as ordered 4-bit patterns
    # (u0,u1,w0,w1) where colors match:
    #   both color0: u in {00,11}, w in {00,11} -> 4 combos
    #   both color1: (01,01) -> 1 combo
    #   both color2: (10,10) -> 1 combo
    # Total 6 monochromatic ordered patterns. OR them onto flag.
    mono_patterns = []
    c0 = [(0, 0), (1, 1)]
    for u in c0:
        for w in c0:
            mono_patterns.append((u[0], u[1], w[0], w[1]))
    mono_patterns.append((0, 1, 0, 1))  # color1,color1
    mono_patterns.append((1, 0, 1, 0))  # color2,color2

    def set_flag_for_edge(u_v, w_v, flag):
        u0, u1 = vb(u_v)
        w0, w1 = vb(w_v)
        ctrls = [u0, u1, w0, w1]
        for pat in mono_patterns:
            # X on lines where pattern bit is 0, mcx, then undo
            zeros = [ctrls[i] for i in range(4) if pat[i] == 0]
            for q in zeros:
                qc.x(q)
            qc.mcx(ctrls, flag)
            for q in zeros:
                qc.x(q)

    # Compute all edge flags.
    for (uu, ww), fl in zip(edges, edge_flags):
        set_flag_for_edge(uu, ww, fl)

    # Now f = 1 iff all edges are NOT mono, i.e. all edge_flags == 0.
    # Apply phase -1 when all flags are 0: X all flags, multi-controlled Z, X back.
    for fl in edge_flags:
        qc.x(fl)
    # multi-controlled Z on the three flags (phase -1 iff all three are 1 now,
    # which corresponds to all originally 0).
    qc.h(edge_flags[2])
    qc.mcx([edge_flags[0], edge_flags[1]], edge_flags[2])
    qc.h(edge_flags[2])
    for fl in edge_flags:
        qc.x(fl)

    # Uncompute edge flags (mirror).
    for (uu, ww), fl in reversed(list(zip(edges, edge_flags))):
        set_flag_for_edge(uu, ww, fl)

    # scratch unused but kept at |0>.
    _ = scratch
