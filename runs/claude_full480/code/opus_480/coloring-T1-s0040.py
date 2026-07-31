from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (1, 2), (1, 3), (2, 3)]

    def vq(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # edge ancillas: one per edge, set to 1 iff the edge is "bad" (same color)
    edge_anc = ancilla_qubits[:4]
    flag = ancilla_qubits[4]

    def color_equal_compute(u, v, anc):
        # colors: c=0(00),1(01),2(10),3(11)->0. So color(a)=color(b) iff
        # decoded colors equal. Decoded: {00,11}->0, 01->1, 10->2.
        # Same color iff (a==b) OR (a,b both in {00,11}).
        # We compute predicate "same color" into anc via helper ancilla-free
        # boolean logic using the two flag/temp qubits. But we only have edge_anc
        # and flag. We'll compute directly onto anc using reversible gates,
        # reusing 'flag' as a scratch that we clean.
        u0, u1 = vq(u)
        v0, v1 = vq(v)
        # We need: same = (u==v) OR (u in {00,11} AND v in {00,11})
        #        = (u==v) OR ((u0==u1) AND (v0==v1))
        # Term A = (u0==v0)AND(u1==v1)  -> exact bit equality
        # Term B = (u0==u1)AND(v0==v1)  -> both codes are "even-color-0" pair
        # same = A OR B.
        # Compute A into anc: A = NOT(u0 xor v0) AND NOT(u1 xor v1)
        # Use flag as scratch for term B, then combine.
        # --- Term A into anc ---
        qc.cx(u0, v0)
        qc.cx(u1, v1)
        qc.x(v0)
        qc.x(v1)
        qc.ccx(v0, v1, anc)   # anc = A
        qc.x(v0)
        qc.x(v1)
        qc.cx(u1, v1)
        qc.cx(u0, v0)
        # --- Term B into flag ---
        qc.cx(u0, u1)         # u1 now = u0 xor u1 ; ==0 iff u0==u1
        qc.cx(v0, v1)
        qc.x(u1)
        qc.x(v1)
        qc.ccx(u1, v1, flag)  # flag = B
        qc.x(u1)
        qc.x(v1)
        qc.cx(v0, v1)
        qc.cx(u0, u1)
        # --- anc = A OR B = NOT( NOT A AND NOT B ) ---
        qc.x(anc)
        qc.x(flag)
        qc.ccx(anc, flag, anc)  # anc = NOTA AND NOTB written where? need fresh
        # The above is wrong to do in place; redo cleanly below.

    # The in-place OR above corrupts anc. Reimplement color_equal cleanly.
    def compute_same(u, v, anc):
        u0, u1 = vq(u)
        v0, v1 = vq(v)
        # anc must start |0>. Compute same = A OR B using De Morgan:
        # same = NOT(NOT A AND NOT B). Put anc = 1 initially, then AND-clear.
        # Step 1: compute A into anc.
        qc.cx(u0, v0)
        qc.cx(u1, v1)
        qc.x(v0)
        qc.x(v1)
        qc.ccx(v0, v1, anc)     # anc = A
        qc.x(v0)
        qc.x(v1)
        qc.cx(u1, v1)
        qc.cx(u0, v0)
        # Step 2: compute B into flag.
        qc.cx(u0, u1)
        qc.cx(v0, v1)
        qc.x(u1)
        qc.x(v1)
        qc.ccx(u1, v1, flag)    # flag = B
        qc.x(u1)
        qc.x(v1)
        qc.cx(v0, v1)
        qc.cx(u0, u1)
        # Step 3: anc = A OR B.
        # A and B are mutually exclusive? If A (u==v) and both in {00,11}
        # then B also true -> not exclusive. So use OR = A + B - A*B.
        # anc currently = A, flag = B. Do: if flag and not anc, set anc.
        qc.x(anc)
        qc.ccx(flag, anc, anc)  # if flag and (NOT A): anc(=NOTA branch)...
        qc.x(anc)
        # Undo flag (uncompute B).
        qc.cx(u0, u1)
        qc.cx(v0, v1)
        qc.x(u1)
        qc.x(v1)
        qc.ccx(u1, v1, flag)
        qc.x(u1)
        qc.x(v1)
        qc.cx(v0, v1)
        qc.cx(u0, u1)

    def uncompute_same(u, v, anc):
        u0, u1 = vq(u)
        v0, v1 = vq(v)
        qc.cx(u0, u1)
        qc.cx(v0, v1)
        qc.x(u1)
        qc.x(v1)
        qc.ccx(u1, v1, flag)
        qc.x(u1)
        qc.x(v1)
        qc.cx(v0, v1)
        qc.cx(u0, u1)
        qc.x(anc)
        qc.ccx(flag, anc, anc)
        qc.x(anc)
        qc.cx(u0, u1)
        qc.cx(v0, v1)
        qc.x(u1)
        qc.x(v1)
        qc.ccx(u1, v1, flag)
        qc.x(u1)
        qc.x(v1)
        qc.cx(v0, v1)
        qc.cx(u0, u1)
        qc.cx(u0, v0)
        qc.cx(u1, v1)
        qc.x(v0)
        qc.x(v1)
        qc.ccx(v0, v1, anc)
        qc.x(v0)
        qc.x(v1)
        qc.cx(u1, v1)
        qc.cx(u0, v0)

    edges_list = edges
    for i, (u, v) in enumerate(edges_list):
        compute_same(u, v, edge_anc[i])

    # f(x)=1 iff all edges are properly colored iff ALL edge_anc == 0.
    # Phase -1 when all edge_anc are 0: X all, multi-controlled Z, X all.
    for a in edge_anc:
        qc.x(a)
    qc.h(edge_anc[-1])
    qc.mcx(edge_anc[:-1], edge_anc[-1])
    qc.h(edge_anc[-1])
    for a in edge_anc:
        qc.x(a)

    for i, (u, v) in reversed(list(enumerate(edges_list))):
        uncompute_same(u, v, edge_anc[i])
