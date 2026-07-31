import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 2), (1, 2), (2, 3), (2, 4), (3, 4)]

    def code_qubits(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # For an edge (u, w), the two vertices are the SAME color iff their
    # decoded colors match. Decoding: c=0 or c=3 -> color 0, c=1 -> color 1,
    # c=2 -> color 2. So color(v) as a function of (b0, b1):
    #   color 1 <=> (b0=1, b1=0)
    #   color 2 <=> (b0=0, b1=1)
    #   color 0 <=> (b0=0,b1=0) or (b0=1,b1=1)  i.e. b0 == b1
    #
    # Two vertices same color:
    #   both color1: u_b0 & ~u_b1 & w_b0 & ~w_b1
    #   both color2: ~u_b0 & u_b1 & ~w_b0 & w_b1
    #   both color0: (u_b0==u_b1) & (w_b0==w_b1)
    #
    # edge_bad = same-color. f = 1 iff NO edge is bad => AND over edges of
    # (NOT same-color). We compute one ancilla per edge = same_color(edge),
    # then the predicate f = AND(NOT e_i). Apply phase -1 when all e_i = 0.
    # Multi-controlled-Z on the edge ancillas with all controls = 0
    # (achieved via X-conjugation) gives -1 exactly when every e_i = 0.

    edge_anc = ancilla_qubits[:len(edges)]
    work = ancilla_qubits[len(edges)]  # one scratch ancilla

    def compute_same_color(u, w, target):
        # target ^= same_color(u, w). target assumed 0 on entry per usage.
        ub0, ub1 = code_qubits(u)
        wb0, wb1 = code_qubits(w)

        # both color 1: ub0 & ~ub1 & wb0 & ~wb1
        qc.x(ub1); qc.x(wb1)
        qc.mcx([ub0, ub1, wb0, wb1], target)
        qc.x(ub1); qc.x(wb1)

        # both color 2: ~ub0 & ub1 & ~wb0 & wb1
        qc.x(ub0); qc.x(wb0)
        qc.mcx([ub0, ub1, wb0, wb1], target)
        qc.x(ub0); qc.x(wb0)

        # both color 0: (ub0==ub1) & (wb0==wb1)
        # sameu = NOT(ub0 xor ub1); use work qubit to hold (ub0 xor ub1)
        qc.cx(ub0, work); qc.cx(ub1, work)   # work = ub0 xor ub1
        qc.cx(wb0, work); qc.cx(wb1, work)   # work = (ub0^ub1) xor (wb0^wb1)
        # both color0 <=> ub0^ub1 = 0 AND wb0^wb1 = 0.
        # Equivalent condition split: need both xors zero. We instead compute
        # via controls: target ^= (NOT xu) & (NOT xw). Recompute xu, xw
        # separately is cleaner. Undo the combined work and do it properly.
        qc.cx(wb1, work); qc.cx(wb0, work)
        qc.cx(ub1, work); qc.cx(ub0, work)   # work back to 0

        # proper: work = ub0 xor ub1
        qc.cx(ub0, work); qc.cx(ub1, work)
        qc.x(work)                            # work = NOT(ub0 xor ub1) = sameu
        # now need target ^= sameu & samew where samew = NOT(wb0 xor wb1).
        # Use wb0,wb1 flipped-xor via ccx chain into another scratch? We only
        # have one work qubit. Encode samew inline with X-conjugation on a
        # temporary reuse: compute samew into target-controls using the fact
        # that samew = NOT(wb0 xor wb1). Build control set with wb parity:
        # target ^= sameu & NOT(wb0 xor wb1)
        #   = sameu & ( (~wb0&~wb1) | (wb0&wb1) )
        # Do the two disjoint cases (they are mutually exclusive):
        qc.x(wb0); qc.x(wb1)
        qc.mcx([work, wb0, wb1], target)      # sameu & ~wb0 & ~wb1
        qc.x(wb0); qc.x(wb1)
        qc.mcx([work, wb0, wb1], target)      # sameu & wb0 & wb1
        qc.x(work)                            # undo NOT
        qc.cx(ub1, work); qc.cx(ub0, work)    # work back to 0

    # compute all edge same-color ancillas
    for (u, w), anc in zip(edges, edge_anc):
        compute_same_color(u, w, anc)

    # phase: -1 iff all edge_anc == 0
    for a in edge_anc:
        qc.x(a)
    if len(edge_anc) == 1:
        qc.z(edge_anc[0])
    else:
        qc.h(edge_anc[-1])
        qc.mcx(edge_anc[:-1], edge_anc[-1])
        qc.h(edge_anc[-1])
    for a in edge_anc:
        qc.x(a)

    # uncompute all edge same-color ancillas (mirror order)
    for (u, w), anc in reversed(list(zip(edges, edge_anc))):
        compute_same_color(u, w, anc)
