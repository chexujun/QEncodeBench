from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 1), (0, 3), (1, 2)]

    def vbits(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # For each edge we compute an "edge_ok" ancilla = 1 iff the two endpoints
    # decode to DIFFERENT colors. Then the overall predicate is AND of all
    # edge_ok bits. We phase-flip when all edge_ok == 1.
    #
    # Decoding: codes 00->0, 01->1, 10->2, 11->0. So colors collide iff:
    #   same 2-bit code (00==00, 01==01, 10==10, 11==11), OR
    #   one endpoint is 00 and the other is 11 (both -> color 0), either order.
    #
    # edge_ok = NOT(collision). We compute collision into the edge ancilla,
    # since we want AND of (NOT collision). Equivalently phase-flip iff no edge
    # has a collision. We'll compute per-edge "bad" flags, OR-free approach:
    # compute "good" edge flag = NOT collision, then multi-controlled Z on all
    # good flags.
    #
    # collision(u,w): let (u0,u1),(w0,w1).
    #   same code: (u0==w0) AND (u1==w1)
    #   00/11 pair: (u0==u1==0 AND w0==w1==1) OR (u0==u1==1 AND w0==w1==0)
    #
    # We build collision into ancilla c using the compute/uncompute discipline,
    # then set good = NOT c (X on c). After the phase, uncompute.

    edge_anc = ancilla_qubits[:len(edges)]

    def compute_collision(u, w, c):
        u0, u1 = vbits(u)
        w0, w1 = vbits(w)
        # Term A: same code. equal bits: e0 = NOT(u0 xor w0), e1 = NOT(u1 xor w1)
        # same = e0 AND e1. We'll accumulate collision = A OR B OR C via the
        # identity: for disjoint terms we can just XOR (the three terms below
        # are mutually exclusive):
        #   A: same code  (includes 00==00, 01,10,11==11 etc.)
        #   B: u=00, w=11
        #   C: u=11, w=00
        # A already contains the 11==11 case; B and C are the cross 00/11 case
        # which is disjoint from A (codes differ). So collision = A xor B xor C.

        # --- Term A: same code ---
        # e0 = NOT(u0 xor w0): put onto u0 temporarily? We must not disturb
        # problem qubits. Use controls directly with an equality trick:
        # same = (u0==w0)&(u1==w1). Use mcx with control_state.
        qc.mcx([u0, w0, u1, w1], c, ctrl_state='0000')  # u0=0,w0=0,u1=0,w1=0 -> both 00
        qc.mcx([u0, w0, u1, w1], c, ctrl_state='1010')  # u0=1,w0=0? careful ordering
        # The control_state string is little-endian over the control list order
        # [u0, w0, u1, w1]; char[0]->u0. We enumerate the 4 same-code cases:
        #   00==00: u0=0,w0=0,u1=0,w1=0
        #   01==01: u0=1,w0=1,u1=0,w1=0
        #   10==10: u0=0,w0=0,u1=1,w1=1
        #   11==11: u0=1,w0=1,u1=1,w1=1
        # We already added 00==00 above (ctrl '0000'). The second line above was
        # wrong; redo cleanly below by flipping c back and doing the real set.
        qc.mcx([u0, w0, u1, w1], c, ctrl_state='1010')  # undo the erroneous one
        qc.mcx([u0, w0, u1, w1], c, ctrl_state='1100')  # 01==01: u0=1,w0=1,u1=0,w1=0
        qc.mcx([u0, w0, u1, w1], c, ctrl_state='0011')  # 10==10: u0=0,w0=0,u1=1,w1=1
        qc.mcx([u0, w0, u1, w1], c, ctrl_state='1111')  # 11==11
        # --- Term B: u=00, w=11 -> u0=0,u1=0,w0=1,w1=1 ---
        qc.mcx([u0, w0, u1, w1], c, ctrl_state='0101')  # u0=0,w0=1,u1=0,w1=1
        # --- Term C: u=11, w=00 -> u0=1,u1=1,w0=0,w1=0 ---
        qc.mcx([u0, w0, u1, w1], c, ctrl_state='1010')  # u0=1,w0=0,u1=1,w1=0

    for (u, w), c in zip(edges, edge_anc):
        compute_collision(u, w, c)
        qc.x(c)  # good = NOT collision

    qc.h(edge_anc[-1])
    qc.mcx(edge_anc[:-1], edge_anc[-1])
    qc.h(edge_anc[-1])

    for (u, w), c in reversed(list(zip(edges, edge_anc))):
        qc.x(c)
        # uncompute collision (mirror)
        u0, u1 = vbits(u)
        w0, w1 = vbits(w)
        qc.mcx([u0, w0, u1, w1], c, ctrl_state='1010')
        qc.mcx([u0, w0, u1, w1], c, ctrl_state='0101')
        qc.mcx([u0, w0, u1, w1], c, ctrl_state='1111')
        qc.mcx([u0, w0, u1, w1], c, ctrl_state='0011')
        qc.mcx([u0, w0, u1, w1], c, ctrl_state='1100')
        qc.mcx([u0, w0, u1, w1], c, ctrl_state='1010')
        qc.mcx([u0, w0, u1, w1], c, ctrl_state='1010')
        qc.mcx([u0, w0, u1, w1], c, ctrl_state='0000')
