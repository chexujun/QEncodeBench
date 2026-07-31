from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 3), (1, 2), (2, 3)]

    # Problem qubit layout: vertex v uses low bit at problem_qubits[2v],
    # high bit at problem_qubits[2v+1]. Color c = b0 + 2*b1, with c==3
    # decoding to color 0 (same as c==0).
    def bits(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # Ancilla plan:
    #   a_edge[k] : per-edge "same color" flag (we reuse a single ancilla
    #               sequentially, but we need one flag per edge to AND them).
    #   We AND all four edge-diff conditions into one accumulator, then phase.
    # ancilla_qubits has 5 qubits: 4 edge flags + 1 accumulator.
    edge_flag = ancilla_qubits[0:4]   # one per edge
    acc = ancilla_qubits[4]           # AND accumulator (predicate)

    def color_equal_compute(u, w, flag):
        """Set flag = 1 iff decoded-color(u) == decoded-color(w).

        Colors in {0,1,2}, with codes: color0 = {00, 11}, color1 = {01},
        color2 = {10}. Two vertices share a color iff:
          - both are color1: u==01 and w==01
          - both are color2: u==10 and w==10
          - both are color0: u in {00,11} and w in {00,11}
        We OR these three mutually-exclusive cases into flag.
        """
        u0, u1 = bits(u)
        w0, w1 = bits(w)

        # Case color1: code == 01  => b0=1, b1=0
        # match u: (u0=1, u1=0) and w: (w0=1, w1=0)
        # Use ancilla-free multi-controlled X with control states via x-conjugation.
        # color1 for a vertex: controls b0=1, b1=0.
        # both color1:
        qc.x(u1); qc.x(w1)
        qc.mcx([u0, u1, w0, w1], flag)
        qc.x(u1); qc.x(w1)

        # Case color2: code == 10 => b0=0, b1=1
        qc.x(u0); qc.x(w0)
        qc.mcx([u0, u1, w0, w1], flag)
        qc.x(u0); qc.x(w0)

        # Case color0: code in {00, 11} => b0 == b1 for each vertex,
        # AND both vertices color0.
        # color0(v) == 1 iff b0 XOR b1 == 0. Compute helper predicates.
        # We express: both color0 iff (u0==u1) and (w0==w1).
        # (u0==u1) == NOT(u0 XOR u1). Build via controlled logic using flag,
        # but we already use flag as OR target; need reversible AND of the two
        # equality predicates. Do it by enumerating the 4 matching code-pairs:
        #   (u=00,w=00),(u=00,w=11),(u=11,w=00),(u=11,w=11)
        for (a0, a1) in [(0, 0), (1, 1)]:      # u code
            for (b0, b1) in [(0, 0), (1, 1)]:  # w code
                # flip controls to match desired 0-values
                flips = []
                if a0 == 0: flips.append(u0)
                if a1 == 0: flips.append(u1)
                if b0 == 0: flips.append(w0)
                if b1 == 0: flips.append(w1)
                for q in flips:
                    qc.x(q)
                qc.mcx([u0, u1, w0, w1], flag)
                for q in flips:
                    qc.x(q)

    # 1) Compute each edge's "same color" flag.
    for k, (u, w) in enumerate(edges):
        color_equal_compute(u, w, edge_flag[k])

    # 2) We want f(x) = 1 iff ALL edges differ, i.e. all edge_flag == 0.
    #    acc = AND over edges of (NOT same) = 1 iff every flag is 0.
    #    Flip all flags so that flag' = NOT same; then acc = AND of flag'.
    for k in range(4):
        qc.x(edge_flag[k])
    qc.mcx(edge_flag, acc)          # acc = 1 iff all flags were "different"
    for k in range(4):
        qc.x(edge_flag[k])

    # 3) Phase: -1 iff acc == 1 (i.e. f(x)==1).
    qc.z(acc)

    # 4) Uncompute acc.
    for k in range(4):
        qc.x(edge_flag[k])
    qc.mcx(edge_flag, acc)
    for k in range(4):
        qc.x(edge_flag[k])

    # 5) Uncompute each edge flag (mirror of compute).
    for k, (u, w) in enumerate(reversed(edges)):
        color_equal_compute(u, w, edge_flag[len(edges) - 1 - k])
