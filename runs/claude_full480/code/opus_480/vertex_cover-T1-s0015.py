from qiskit import QuantumCircuit
from math import pi


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = (problem_qubits[0], problem_qubits[1],
                      problem_qubits[2], problem_qubits[3])
    edges = [(0, 1), (0, 2), (1, 2), (2, 3)]

    edge_anc = ancilla_qubits[0:4]   # one per edge: covered flag
    cnt_anc = ancilla_qubits[4:6]    # 2-bit popcount (values 0..4 need 3 bits; but <=2 check uses carry)
    ok_anc = ancilla_qubits[6]

    # --- compute edge-covered flags: covered = a OR b = NOT(NOT a AND NOT b) ---
    for idx, (u, v) in enumerate(edges):
        qu = problem_qubits[u]
        qv = problem_qubits[v]
        e = edge_anc[idx]
        qc.x(qu)
        qc.x(qv)
        qc.ccx(qu, qv, e)   # e = (NOT u)(NOT v) = uncovered
        qc.x(qu)
        qc.x(qv)
        qc.x(e)             # e = covered

    # --- compute popcount of x0..x3 into a 3-bit counter using ripple adders ---
    # counter bits: c0 (LSB), c1, c2 ; we only need to know if popcount <= 2,
    # i.e. NOT(popcount >= 3). popcount>=3 means c1&(c0|... ) ; use full sum.
    # Build sum via successive half/full adders into cnt_anc + ok_anc as temp.
    # We use cnt_anc[0]=s0, cnt_anc[1]=s1, ok_anc temporarily as s2.
    s0 = cnt_anc[0]
    s1 = cnt_anc[1]
    s2 = ok_anc  # temp for carry (will be cleaned; final phase uses le2 flag computed differently)

    def add_bit(b):
        # add problem bit b into (s2,s1,s0) counter
        # new carry to s1: s0 & b ; then s0 ^= b
        # then carry into s2: s1 & carry ; s1 ^= carry
        qc.ccx(s0, b, s1)       # this is wrong ordering if reused; handled by sequence
        qc.cx(b, s0)
    # The above naive approach corrupts; instead do explicit correct ripple:

    # Reset plan: we abandon add_bit; do manual correct increments.
    # Undo the stray gates from add_bit definition? It's only a def, not called. Good.

    # Manual popcount: increment counter (s1,s0) for each of 4 bits, and track >=3 in s2.
    for b in (x0, x1, x2, x3):
        # carry1 = s0 & b -> propagate to s1; but need carry from s1 into s2 too
        qc.ccx(s1, s0, s2)   # if s1&s0 already set and about to overflow... (2->3 detection)
        # increment: standard controlled increment of 2-bit (s1,s0) by b
        qc.ccx(b, s0, s1)    # s1 ^= b & s0  (carry)
        qc.cx(b, s0)         # s0 ^= b
        qc.ccx(s1, s0, s2)   # detect reaching >=3

    # s2 now flags popcount>=3 (le2 violated). le2 = NOT s2.

    # --- final predicate: all edges covered AND popcount<=2 ---
    controls = list(edge_anc)  # all must be 1
    qc.x(s2)                   # s2 = le2
    controls.append(s2)
    qc.h(controls[-1]) if False else None
    qc.mcx(controls[:-1] + [s2], ancilla_qubits[6] if False else s0) if False else None

    # phase via multi-controlled Z on (4 edge flags + le2)
    qc.mcp(pi, controls[:-1], controls[-1])

    qc.x(s2)  # restore s2 to popcount>=3 flag for uncompute

    # --- uncompute popcount ---
    for b in (x3, x2, x1, x0):
        qc.ccx(s1, s0, s2)
        qc.cx(b, s0)
        qc.ccx(b, s0, s1)
        qc.ccx(s1, s0, s2)

    # --- uncompute edge flags ---
    for idx, (u, v) in enumerate(edges):
        qu = problem_qubits[u]
        qv = problem_qubits[v]
        e = edge_anc[idx]
        qc.x(e)
        qc.x(qu)
        qc.x(qv)
        qc.ccx(qu, qv, e)
        qc.x(qu)
        qc.x(qv)
