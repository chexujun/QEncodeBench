from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    import math

    edges = [(0, 1), (0, 2), (0, 3), (1, 2)]

    def qb(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # ancilla layout: 4 edge-flag ancillas + 1 phase ancilla
    edge_anc = ancilla_qubits[0:4]
    phase_anc = ancilla_qubits[4]

    def edge_same_color(a_lo, a_hi, b_lo, b_hi, out, invert=False):
        # Set `out` ^= 1 iff decoded(a) == decoded(b).
        # decode: 00->0, 01->1, 10->2, 11->0  (11 aliases to 00)
        # Same color cases (ordered pairs of codes) with same decoded color:
        #   (00,00),(00,11),(11,00),(11,11) -> color 0
        #   (01,01)                         -> color 1
        #   (10,10)                         -> color 2
        # We compute equality of decoded colors via a small set of MCX terms
        # over the 4 code bits (a_hi,a_lo,b_hi,b_lo).
        # Enumerate the 4-bit patterns where decoded colors are equal:
        #   a in {00,11}, b in {00,11}  (both color 0)
        #   a=01, b=01                  (both color 1)
        #   a=10, b=10                  (both color 2)
        # Pattern bits order for controls: a_lo,a_hi,b_lo,b_hi
        same_patterns = [
            (0, 0, 0, 0),
            (0, 0, 1, 1),
            (1, 1, 0, 0),
            (1, 1, 1, 1),
            (1, 0, 1, 0),
            (0, 1, 0, 1),
        ]
        ctrls = [a_lo, a_hi, b_lo, b_hi]
        for pat in same_patterns:
            zeros = [ctrls[i] for i, bit in enumerate(pat) if bit == 0]
            for q in zeros:
                qc.x(q)
            qc.mcx(ctrls, out)
            for q in zeros:
                qc.x(q)

    # Compute: for each edge, flag = 1 iff endpoints share a color (BAD).
    for k, (u, v) in enumerate(edges):
        u_lo, u_hi = qb(u)
        v_lo, v_hi = qb(v)
        edge_same_color(u_lo, u_hi, v_lo, v_hi, edge_anc[k])

    # f(x)=1 iff ALL edges are properly colored, i.e. all edge flags == 0.
    # phase_anc = 1 iff all flags are 0. Flip flags, MCX, flip back.
    for k in range(4):
        qc.x(edge_anc[k])
    qc.mcx(edge_anc, phase_anc)
    for k in range(4):
        qc.x(edge_anc[k])

    # Phase: -1 iff phase_anc == 1 (i.e. f(x)=1)
    qc.z(phase_anc)

    # Uncompute phase_anc
    for k in range(4):
        qc.x(edge_anc[k])
    qc.mcx(edge_anc, phase_anc)
    for k in range(4):
        qc.x(edge_anc[k])

    # Uncompute edge flags (mirror)
    for k, (u, v) in enumerate(reversed(edges)):
        idx = 3 - k
        u_lo, u_hi = qb(u)
        v_lo, v_hi = qb(v)
        edge_same_color(u_lo, u_hi, v_lo, v_hi, edge_anc[idx])
