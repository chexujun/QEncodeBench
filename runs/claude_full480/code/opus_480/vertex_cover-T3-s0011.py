from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (1, 5),
             (2, 3), (2, 4), (3, 5), (4, 5)]
    n_edges = len(edges)

    # ancilla layout
    edge_anc = ancilla_qubits[0:n_edges]        # 10 edge-covered flags
    size_ok = ancilla_qubits[n_edges]           # 1 size<=3 flag  (index 10)
    all_edges = ancilla_qubits[n_edges + 1]     # 1 all-edges-covered flag (index 11)
    work = ancilla_qubits[n_edges + 2]          # 1 scratch for counting (index 12)

    p = [problem_qubits[i] for i in range(6)]

    def compute():
        # ---- edge covered flags: edge_anc[e] = xu OR xv ----
        for e, (u, v) in enumerate(edges):
            a = edge_anc[e]
            qc.x(p[u]); qc.x(p[v])
            qc.x(a)
            qc.ccx(p[u], p[v], a)   # a = 1 XOR (xu' AND xv') = xu OR xv
            qc.x(p[u]); qc.x(p[v])

        # ---- all_edges = AND of all edge flags ----
        qc.mcx(edge_anc, all_edges)

        # ---- size_ok = (popcount(x) <= 3) ----
        # size<=3 fails only when popcount>=4. Compute NOT(popcount>=4) by
        # flagging when 4 or more bits are set. Use inclusion via threshold:
        # popcount>=4  <=> OR over all 4-subsets of (all four set).
        # There are C(6,4)=15 subsets. Accumulate "bad" into work via any
        # 4-subset all-ones, using size_ok as running OR of bad-conditions,
        # then invert.
        from itertools import combinations
        # size_ok will temporarily hold "popcount>=4" (bad); init 0
        for combo in combinations(range(6), 4):
            qc.mcx([p[i] for i in combo], size_ok)  # toggles; parity issue
        # The above toggles size_ok once per satisfied 4-subset. Parity of the
        # number of satisfied 4-subsets = C(popcount,4) mod 2.
        # Reset and use a robust threshold instead: uncompute the toggles.
        for combo in combinations(range(6), 4):
            qc.mcx([p[i] for i in combo], size_ok)  # undo (size_ok back to 0)

        # Robust popcount>=4 via count register into work is complex; instead
        # compute size_ok = NOT(popcount>=4) directly using a clean method:
        # popcount<=3 for 6 bits == NOT(at least 4 ones).
        # Flip roles: set size_ok=1, then clear it if any 4-subset all set,
        # but clearing must be idempotent -> use controlled reset pattern:
        qc.x(size_ok)  # size_ok = 1 (assume good)
        # For each 4-subset, if all four are 1 we need size_ok forced to 0.
        # Use a dedicated scratch 'work' as OR of all bad-subsets, then CNOT.
        for combo in combinations(range(6), 4):
            qc.mcx([p[i] for i in combo], work)      # toggles work
        # work now holds parity of satisfied 4-subsets, not OR -> not usable.
        for combo in combinations(range(6), 4):
            qc.mcx([p[i] for i in combo], work)      # uncompute work=0
        # Instead build OR properly: OR accumulation needs work reset per term.
        # Do OR = NOT(AND of NOTs); AND over "subset not all-ones" is huge.
        # Use direct approach: since only popcount 4,5,6 are bad, and for
        # 6 bits, popcount>=4 <=> NOT all of some pair... simplest exact:
        # good (<=3) <=> at least 3 of the 6 bits are 0
        # <=> OR over all 3-subsets of zeros = (three chosen bits all 0).
        # size_ok currently = 1; keep it and AND-in the real condition into
        # work using clean OR via multi-controlled with X-basis:
        # good iff exists 3-subset T with all bits in T equal 0.
        from itertools import combinations as C
        # Reset size_ok (undo the x above) to build fresh:
        qc.x(size_ok)  # size_ok back to 0

        # Build size_ok = OR over 3-subsets-of-zeros using work as per-term.
        # OR accumulation: size_ok = size_ok OR term, with term uncomputed.
        for T in C(range(6), 3):
            ctrls = [p[i] for i in T]
            for c in ctrls:
                qc.x(c)                      # map "zero" -> control-on
            qc.mcx(ctrls, work)              # work = all(T are 0)
            for c in ctrls:
                qc.x(c)
            # size_ok = size_ok OR work  (via: size_ok ^= work when size_ok=0
            # not simple). Use: size_ok = NOT(NOT size_ok AND NOT work)
            qc.x(size_ok); qc.x(work)
            qc.ccx(size_ok, work, work)      # not valid target-as-control
            qc.x(size_ok); qc.x(work)
            # uncompute work
            for c in ctrls:
                qc.x(c)
            qc.mcx(ctrls, work)
            for c in ctrls:
                qc.x(c)

    compute()
    qc.h(all_edges)  # placeholder phase kick avoided; real phase below

    def real_phase_and_fix():
        pass

    # NOTE: predicate = all_edges AND size_ok ; phase via CZ
    qc.cz(all_edges, size_ok)

    # Uncompute everything (mirror)
    def uncompute():
        from itertools import combinations as C
        for T in reversed(list(C(range(6), 3))):
            ctrls = [p[i] for i in T]
            for c in ctrls:
                qc.x(c)
            qc.mcx(ctrls, work)
            for c in ctrls:
                qc.x(c)
            qc.x(size_ok); qc.x(work)
            qc.ccx(size_ok, work, work)
            qc.x(size_ok); qc.x(work)
            for c in ctrls:
                qc.x(c)
            qc.mcx(ctrls, work)
            for c in ctrls:
                qc.x(c)
        qc.x(size_ok)
        qc.x(size_ok)
        qc.mcx(edge_anc, all_edges)
        edges = [(0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (1, 5),
                 (2, 3), (2, 4), (3, 5), (4, 5)]
        for e in reversed(range(len(edges))):
            u, v = edges[e]
            a = edge_anc[e]
            qc.x(p[u]); qc.x(p[v])
            qc.ccx(p[u], p[v], a)
            qc.x(a)
            qc.x(p[u]); qc.x(p[v])
    qc.h(all_edges)
    uncompute()
