from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 1), (1, 2), (2, 3)]

    def vq(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # ancilla[i] will hold "edge i is monochromatic (same decoded color)"
    edge_anc = [ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]]
    final = ancilla_qubits[3]

    def compute_edge_mono(u, w, anc, tmp):
        # decoded color equal iff:
        #   (cu==cw)  OR  (cu,cw) in {0,3} pair, i.e. both decode to color 0.
        # color(c): c=0->0, c=1->1, c=2->2, c=3->0.
        # Two vertices share color iff:
        #   (a) exact code match cu==cw, OR
        #   (b) {cu,cw} == {0,3} (one is 00, other is 11), OR
        #       cu==cw==0 or cu==cw==3 already covered by (a).
        # So mono iff codes equal, OR (one code is 00 and other is 11),
        #   OR (one is 00 and other is 00) [covered], etc.
        # Enumerate decoded-equal code pairs (cu,cw):
        #   color0 codes: {00, 11}; color1: {01}; color2: {10}.
        # mono iff both in {00,11}, or both ==01, or both ==10.
        u0, u1 = vq(u)
        w0, w1 = vq(w)
        # We set anc=1 for each of these disjoint OR-terms:
        #  term A: both codes in {00,11}
        #     code in {00,11} iff b0==b1. Let pu = (u0==u1), pw=(w0==w1).
        #     A = pu AND pw.
        #  term B: both ==01  -> u0=1,u1=0 and w0=1,w1=0
        #  term C: both ==10  -> u0=0,u1=1 and w0=0,w1=1
        # These three are mutually exclusive, so OR = sum (XOR into anc works).

        # --- term A: pu = NOT(u0 XOR u1), pw = NOT(w0 XOR w1) ---
        # compute pu into tmp[0], pw into tmp[1]
        pu = tmp[0]
        pw = tmp[1]
        qc.cx(u0, pu); qc.cx(u1, pu); qc.x(pu)   # pu = 1 iff u0==u1
        qc.cx(w0, pw); qc.cx(w1, pw); qc.x(pw)   # pw = 1 iff w0==w1
        qc.ccx(pu, pw, anc)                      # anc ^= A
        # uncompute pu, pw
        qc.x(pw); qc.cx(w1, pw); qc.cx(w0, pw)
        qc.x(pu); qc.cx(u1, pu); qc.cx(u0, pu)

        # --- term B: both ==01 (b0=1,b1=0) ---
        qc.x(u1); qc.x(w1)
        qc.mcx([u0, u1, w0, w1], anc)
        qc.x(u1); qc.x(w1)

        # --- term C: both ==10 (b0=0,b1=1) ---
        qc.x(u0); qc.x(w0)
        qc.mcx([u0, u1, w0, w1], anc)
        qc.x(u0); qc.x(w0)

    tmp = [ancilla_qubits[3], ancilla_qubits[2]]  # reuse as scratch during compute; but need care

    # We need clean scratch qubits. Use edge_anc[2] and final as scratch only
    # while they are not yet holding edge results. To keep discipline simple,
    # process edges sequentially, each fully compute->store->uncompute-scratch,
    # accumulate the "any monochromatic" into final via the edge ancillas.

    # Compute each edge's mono flag using two scratch qubits.
    # Scratch qubits: we need 2 clean ones distinct from the edge flag being set.
    scratch = [ancilla_qubits[3], ancilla_qubits[2]]

    # Edge 0 -> flag in edge_anc[0]; scratch: final(3) and edge_anc[2](2)
    compute_edge_mono(0, 1, edge_anc[0], [ancilla_qubits[3], ancilla_qubits[2]])
    # Edge 1 -> flag in edge_anc[1]; scratch: final(3) and edge_anc[2](2)
    compute_edge_mono(1, 2, edge_anc[1], [ancilla_qubits[3], ancilla_qubits[2]])
    # Edge 2 -> flag in edge_anc[2]; scratch: final(3) and edge_anc[0]? conflict.
    #   use scratch final(3) and edge_anc[1]? edge_anc[1] holds a result -> no.
    # Need two clean scratch qubits for edge 2. Only 'final' is clean now.
    # So compute edge 2 differently, needing only ONE scratch qubit.
    def compute_edge_mono_1scratch(u, w, anc, s):
        u0, u1 = vq(u); w0, w1 = vq(w)
        # term A with single scratch: pu into s, then need pw too -> can't hold both.
        # Reformulate A = pu AND pw where pu=(u0==u1), pw=(w0==w1).
        # A holds iff (u0 XOR u1)==0 and (w0 XOR w1)==0, i.e. all-zero of
        # {u0^u1, w0^w1}. Fold u1->u0-slot and w1->w0-slot temporarily:
        qc.cx(u1, u0)   # u0 now = u0^u1 (temp)
        qc.cx(w1, w0)   # w0 now = w0^w1 (temp)
        qc.x(u0); qc.x(w0)
        qc.ccx(u0, w0, anc)   # anc ^= (u0^u1==0 AND w0^w1==0) = A
        qc.x(u0); qc.x(w0)
        qc.cx(w1, w0)   # restore w0
        qc.cx(u1, u0)   # restore u0
        # term B: both ==01
        qc.x(u1); qc.x(w1)
        qc.mcx([u0, u1, w0, w1], anc)
        qc.x(u1); qc.x(w1)
        # term C: both ==10
        qc.x(u0); qc.x(w0)
        qc.mcx([u0, u1, w0, w1], anc)
        qc.x(u0); qc.x(w0)

    compute_edge_mono_1scratch(2, 3, edge_anc[2], ancilla_qubits[3])

    # Now edge_anc[0..2] hold monochromatic flags. f(x)=1 iff ALL edges are
    # properly colored, i.e. NO edge is monochromatic: all three flags == 0.
    # Phase -1 iff (m0==0 AND m1==0 AND m2==0).
    qc.x(edge_anc[0]); qc.x(edge_anc[1]); qc.x(edge_anc[2])
    # multi-controlled Z on all-ones-of-(NOT flags) with a Z via H-mcx-H on final
    qc.h(final)
    qc.mcx([edge_anc[0], edge_anc[1], edge_anc[2]], final)
    qc.h(final)
    qc.x(edge_anc[0]); qc.x(edge_anc[1]); qc.x(edge_anc[2])

    # Uncompute edge flags (mirror the compute in reverse order).
    compute_edge_mono_1scratch(2, 3, edge_anc[2], ancilla_qubits[3])
    compute_edge_mono(1, 2, edge_anc[1], [ancilla_qubits[3], ancilla_qubits[2]])
    compute_edge_mono(0, 1, edge_anc[0], [ancilla_qubits[3], ancilla_qubits[2]])
