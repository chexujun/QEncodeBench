from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Vertex v uses qubits problem_qubits[2v] (b0) and problem_qubits[2v+1] (b1).
    # Colors: c=0(00)->0, c=1(01)->1, c=2(10)->2, c=3(11)->0.
    # Two vertices share a color iff their decoded colors are equal.
    #
    # Decoded color as function of (b0,b1):
    #   color 0 <-> (b0,b1) in {00, 11}
    #   color 1 <-> (b0,b1) == 01  (b0=1,b1=0)
    #   color 2 <-> (b0,b1) == 10  (b0=0,b1=1)
    #
    # For an edge (u,v) let (a0,a1) be u's bits, (c0,c1) be v's bits.
    # "same color" predicate S(u,v):
    #   both color0: (a0==a1) and (c0==c1)
    #   both color1: (a0=1,a1=0) and (c0=1,c1=0)
    #   both color2: (a0=0,a1=1) and (c0=0,c1=1)
    #
    # f = 1 iff for every edge, NOT same color = all edges are "differ".
    # We compute per-edge a "same" flag into an ancilla, OR them, then phase
    # when the OR is 0 (all differ). We'll instead compute per-edge "differ"
    # and AND them, phasing when AND==1.
    #
    # Strategy: compute per-edge same-flag e_j into ancilla flags; the mark
    # condition f=1 requires ALL e_j == 0. Phase = -1 iff all same-flags are 0.
    # Use one ancilla per edge to hold "same" flag, then a multi-controlled
    # phase on all-zero of these flags (achieved by X-sandwiching).

    edges = [(0, 1), (0, 2), (1, 2)]
    flags = ancilla_qubits[:3]  # one per edge; 4th ancilla free as scratch

    def bits(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    def compute_same(u, v, flag):
        a0, a1 = bits(u)
        c0, c1 = bits(v)
        # both color1: a0=1,a1=0,c0=1,c1=0  -> controls: a0=1,a1=0,c0=1,c1=0
        # both color2: a0=0,a1=1,c0=0,c1=1
        # both color0: (a0==a1) and (c0==c1): enumerate the two-per-side
        #   (a0,a1) in {(0,0),(1,1)}, (c0,c1) in {(0,0),(1,1)} -> 4 combos
        #
        # We toggle flag once for each (u-color, v-color) matching pair.
        # Since color assignments per vertex are mutually exclusive over the
        # 4 codes, at most one term fires, so XOR-toggling == OR here.

        # both color1
        qc.x(a1); qc.x(c1)
        qc.mcx([a0, a1, c0, c1], flag)
        qc.x(a1); qc.x(c1)

        # both color2
        qc.x(a0); qc.x(c0)
        qc.mcx([a0, a1, c0, c1], flag)
        qc.x(a0); qc.x(c0)

        # both color0: (a0,a1) in {00,11} x (c0,c1) in {00,11}
        for (na0, na1) in [(0, 0), (1, 1)]:
            for (nc0, nc1) in [(0, 0), (1, 1)]:
                if na0 == 0: qc.x(a0)
                if na1 == 0: qc.x(a1)
                if nc0 == 0: qc.x(c0)
                if nc1 == 0: qc.x(c1)
                qc.mcx([a0, a1, c0, c1], flag)
                if na0 == 0: qc.x(a0)
                if na1 == 0: qc.x(a1)
                if nc0 == 0: qc.x(c0)
                if nc1 == 0: qc.x(c1)

    # compute all same-flags
    for (u, v), fl in zip(edges, flags):
        compute_same(u, v, fl)

    # f = 1 iff all flags == 0. Phase -1 on all-flags-zero:
    # X all flags -> multi-controlled Z -> X all flags.
    for fl in flags:
        qc.x(fl)
    # multi-controlled Z on flags: use mcp(pi)
    qc.h(flags[-1])
    qc.mcx(flags[:-1], flags[-1])
    qc.h(flags[-1])
    for fl in flags:
        qc.x(fl)

    # uncompute all same-flags (mirror)
    for (u, v), fl in zip(edges, flags):
        compute_same(u, v, fl)
