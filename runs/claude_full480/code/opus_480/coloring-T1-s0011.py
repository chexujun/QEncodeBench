import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Vertex v uses problem_qubits[2v] (b0) and problem_qubits[2v+1] (b1).
    # Color(v): c=0->0, c=1->1, c=2->2, c=3->0. So color 0 iff code in {00,11},
    # color 1 iff code==01, color 2 iff code==10.
    #
    # Edges: (0,1),(0,2),(0,3). f=1 iff all 3 edges have differing colors.
    # We compute, per edge, an ancilla = 1 iff SAME color (bad), then the
    # predicate "good" = AND of (edge not bad). We phase-flip when good.
    #
    # good = product over edges of (1 - bad_e). Since bad_e are 0/1, and we
    # want phase -1 exactly when all bad_e == 0, i.e. all "not bad" ancillas =1.
    #
    # Strategy: for each edge compute bad_e into an edge-ancilla (bad=1 if same
    # color). Then apply a multi-controlled-Z that flips phase iff ALL edge
    # ancillas are 0 -> wrap with X so control-on-zero.

    def vbits(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # same-color predicate for two vertices u,w into ancilla `anc`.
    # colors: A = color0 = (b0,b1) in {00,11}; equivalently b0==b1.
    #         color1 = 01 -> b0=1,b1=0 ; color2 = 10 -> b0=0,b1=1.
    # same color iff:
    #   both color0: (b0u==b1u) AND (b0w==b1w)
    #   both color1: b0u&~b1u & b0w&~b1w
    #   both color2: ~b0u&b1u & ~b0w&b1w
    # We'll compute each of the 3 "both" terms into a temp ancilla and OR them.
    #
    # To keep it clean and reversible with only the ancillas provided (4 total,
    # 3 needed as edge-flags), we compute each edge's bad flag using a small
    # reversible routine that toggles the edge ancilla for each matching case.
    # The three cases are mutually exclusive, so toggling (cx-style via mcx)
    # for each case sets the flag to OR of cases.

    def compute_same(u, w, anc, uncompute=False):
        b0u, b1u = vbits(u)
        b0w, b1w = vbits(w)

        # Case both color1: b0u=1,b1u=0,b0w=1,b1w=0
        qc.x(b1u); qc.x(b1w)
        qc.mcx([b0u, b1u, b0w, b1w], anc)
        qc.x(b1u); qc.x(b1w)

        # Case both color2: b0u=0,b1u=1,b0w=0,b1w=1
        qc.x(b0u); qc.x(b0w)
        qc.mcx([b0u, b1u, b0w, b1w], anc)
        qc.x(b0u); qc.x(b0w)

        # Case both color0: b0u==b1u and b0w==b1w.
        # both color0 means (b0u xor b1u)==0 and (b0w xor b1w)==0.
        # Toggle anc when all four "equality" conditions hold. Compute equality
        # bits into b1u,b1w temporarily via cx from b0 (b1 becomes b0 xor b1),
        # then require those xors ==0 (i.e. controls-on-zero via X wrap).
        qc.cx(b0u, b1u)   # b1u -> b0u xor b1u
        qc.cx(b0w, b1w)   # b1w -> b0w xor b1w
        qc.x(b1u); qc.x(b1w)      # now =1 iff xor was 0 (equal)
        qc.mcx([b1u, b1w], anc)   # toggle if both equal (both color0)
        qc.x(b1u); qc.x(b1w)
        qc.cx(b0w, b1w)   # restore b1w
        qc.cx(b0u, b1u)   # restore b1u

    edges = [(0, 1), (0, 2), (0, 3)]
    flags = ancilla_qubits[0:3]

    # compute all edge same-color flags
    for (u, w), anc in zip(edges, flags):
        compute_same(u, w, anc)

    # good iff all flags == 0 -> phase -1. Control-on-zero via X wrap + mcp(pi).
    qc.x(flags[0]); qc.x(flags[1]); qc.x(flags[2])
    qc.h(flags[2])
    qc.mcx([flags[0], flags[1]], flags[2])
    qc.h(flags[2])
    qc.x(flags[0]); qc.x(flags[1]); qc.x(flags[2])

    # uncompute flags (mirror)
    for (u, w), anc in zip(reversed(edges), reversed(flags)):
        compute_same(u, w, anc)
