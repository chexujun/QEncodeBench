from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    edges = [(0, 1), (0, 2), (0, 3), (1, 2), (2, 4), (3, 4)]

    # Ancilla layout: 6 edge-cover ancillas, 1 count-ok ancilla, 2 scratch.
    edge_anc = ancilla_qubits[0:6]
    count_ok = ancilla_qubits[6]
    s0 = ancilla_qubits[7]  # weight bit 0 (LSB)
    s1 = ancilla_qubits[8]  # weight bit 1

    def compute():
        # Each edge ancilla = OR(u, v) = 1 iff edge covered.
        # OR(u,v) via: a = u XOR v XOR (u AND v) -> implement as a=u, a^=v, ccx adds u&v back? 
        # Simpler: a = 1 - (1-u)(1-v). Compute NOT(u) & NOT(v) then flip.
        for anc, (u, v) in zip(edge_anc, edges):
            qc.x(x[u]); qc.x(x[v])
            qc.ccx(x[u], x[v], anc)  # anc = (NOT u)AND(NOT v) after flips? no, ccx uses current values
            qc.x(x[u]); qc.x(x[v])
            qc.x(anc)  # anc = NOT( (NOT u) AND (NOT v) ) = u OR v
        # Weight = popcount(x0..x4) into 3-bit register (s1 s0) up to 5.
        # Use ripple: add each xi to (s1,s0) as a 2-bit counter, but max 5 needs 3 bits.
        # k<=3 means NOT(weight>=4) = NOT(weight in {4,5}). Track carry into a 3rd implicit via count_ok directly.
        # Build weight bits s0,s1 and a top bit using count_ok temporarily as bit2, then set count_ok.
        # Add x0..x4 into (s1,s0,c2) where c2 stored on count_ok during compute.
        b2 = count_ok
        for xi in x:
            # full-add xi into s0 with carry chain s0->s1->b2
            qc.ccx(s0, s1, b2)        # carry from bit0&bit1 into bit2 when incrementing? use standard increment
            qc.ccx(xi, s0, s1)        # placeholder gates below replaced by proper increment
    # NOTE: the increment above is not correct; use explicit controlled-increment instead.

    # --- Correct implementation using controlled increment of a 3-bit counter ---
    qc.data  # no-op reference

    def inc(ctrl, b0, b1, b2):
        # increment 3-bit (b2 b1 b0) by 1, controlled on ctrl
        qc.ccx(ctrl, b1, b2)  # will be gated properly below
    # Rebuild cleanly:
    b2 = count_ok
    # zero-start counter; add each xi with a controlled increment (Toffoli cascade)
    for xi in x:
        qc.ccx(xi, s1, b2)   # if xi and s1: carry into b2
        qc.ccx(xi, s0, s1)   # if xi and s0: carry into s1
        qc.cx(xi, s0)        # add xi into s0
    # Now (b2,s1,s0) = weight. Predicate weight<=3  <=> b2==0 AND NOT(s1 AND s0)
    #   weight in 0..5: b2=1 means >=4. b2=0 & s1=1 & s0=1 -> 3 (ok). So >=4 exactly when b2=1.
    # Thus count condition = (b2 == 0).
    # All edges covered = all edge_anc == 1.

    # Phase: -1 iff (all edge_anc==1) AND (b2==0).
    qc.x(b2)  # now b2=1 means count ok
    ctrls = edge_anc + [b2]
    qc.h(ctrls[-1])
    qc.mcx(ctrls[:-1], ctrls[-1])
    qc.h(ctrls[-1])
    qc.x(b2)

    # Uncompute counter (reverse order).
    for xi in reversed(x):
        qc.cx(xi, s0)
        qc.ccx(xi, s0, s1)
        qc.ccx(xi, s1, b2)

    # Uncompute edge ancillas (reverse).
    for anc, (u, v) in zip(reversed(edge_anc), reversed(edges)):
        qc.x(anc)
        qc.x(x[u]); qc.x(x[v])
        qc.ccx(x[u], x[v], anc)
        qc.x(x[u]); qc.x(x[v])
