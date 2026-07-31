import numpy as np
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits
    edges = [(0, 3), (1, 2), (1, 3)]

    # Ancilla layout:
    #   e-ancillas (one per edge): mark "edge covered"
    #   count-ancillas: 3-bit popcount of x (need to check <= 2, i.e. not all-of-any-3? no: <=2 means NOT weight>=3)
    # We have 6 ancillas: 3 for edge-coverage, and 3 for weight bookkeeping.
    edge_anc = [ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]]
    # weight ancillas: we need to detect popcount(x) <= 2 over 4 bits.
    # popcount ranges 0..4. weight<=2 means NOT(weight in {3,4}).
    # Build a 3-bit adder sum of the 4 problem bits into w (bits w0,w1,w2).
    w = [ancilla_qubits[3], ancilla_qubits[4], ancilla_qubits[5]]
    prob = [x0, x1, x2, x3]

    def compute():
        # ---- edge coverage: edge covered iff (a OR b) = NOT(NOT a AND NOT b) ----
        for i, (a, b) in enumerate(edges):
            qa, qb, qe = prob[a], prob[b], edge_anc[i]
            # set qe = a OR b : start qe=0; qe ^= a; qe ^= b; qe ^= (a AND b)
            qc.cx(qa, qe)
            qc.cx(qb, qe)
            qc.ccx(qa, qb, qe)  # OR = a xor b xor (a and b)

        # ---- popcount of the 4 problem bits into w (little-endian w0 lsb) ----
        # ripple: for each input bit, add 1 to the 3-bit counter w conditioned on the bit.
        for q in prob:
            # controlled increment of 3-bit register w by 1, controlled on q
            # carry chain: increment adds 1 to lsb.
            # w2 ^= q & w1 & w0
            qc.mcx([q, w[0], w[1]], w[2])
            # w1 ^= q & w0
            qc.ccx(q, w[0], w[1])
            # w0 ^= q
            qc.cx(q, w[0])

    compute()

    # ---- phase: mark f=1 iff all edges covered AND weight <= 2 ----
    # all edges covered: edge_anc all == 1.
    # weight <= 2 : weight in {0,1,2}, i.e. NOT(w2==1) and NOT(w1==1 and w0==1)
    #   weight value = w0 + 2*w1 + 4*w2. <=2 means w2==0 AND (w1,w0) != (1,1).
    # Predicate P = e0 & e1 & e2 & (~w2) & ~(w1 & w0)
    # Apply phase -1 on states with P true using a multi-controlled Z with
    # appropriate control polarities. Use extra flag on an edge ancilla? We
    # need one target; use mcp(pi) with controls, encoding negative controls
    # by X-conjugation.

    # Negative controls on w2; and we must exclude (w1&w0) both 1.
    # Split ~(w1&w0) is not a single control condition. Handle by summing:
    # P = A & ~(w1 & w0), where A = e0&e1&e2&~w2.
    # phase(-1) on A & ~(w1&w0) = phase on [A] minus phase on [A & w1 & w0].
    # Apply Z (pi phase) to A with all its controls, then undo the pi phase on
    # the A & w1 & w0 subset (apply +pi there, net 0) -> net: phase only where
    # A true and not(w1&w0). Two mcp calls.

    # controls for A: e0,e1,e2 positive ; w2 negative.
    qc.x(w[2])
    # mcp pi on (e0,e1,e2,w2') -> A
    qc.mcp(np.pi, [edge_anc[0], edge_anc[1], edge_anc[2], w[2]], w[0])
    # subtract: mcp pi on (e0,e1,e2,w2', w1, w0-as-control)... need target distinct.
    # Use w[1] region: controls e0,e1,e2,w2',w0 ; target phase gate acts on w1.
    qc.mcp(-np.pi, [edge_anc[0], edge_anc[1], edge_anc[2], w[2], w[0]], w[1])
    qc.x(w[2])

    # ---- uncompute (mirror) ----
    def uncompute():
        for q in reversed(prob):
            qc.cx(q, w[0])
            qc.ccx(q, w[0], w[1])
            qc.mcx([q, w[0], w[1]], w[2])
        for i, (a, b) in reversed(list(enumerate(edges))):
            qa, qb, qe = prob[a], prob[b], edge_anc[i]
            qc.ccx(qa, qb, qe)
            qc.cx(qb, qe)
            qc.cx(qa, qe)

    uncompute()
