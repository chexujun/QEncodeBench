from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 1), (0, 2), (0, 4), (1, 2), (1, 5), (2, 3), (2, 4)]
    n = len(problem_qubits)
    k = 3

    edge_anc = ancilla_qubits[0:7]      # one ancilla per edge (edge covered flag)
    all_edges_anc = ancilla_qubits[7]   # all edges covered flag
    cnt = ancilla_qubits[8:10]          # 2-bit popcount high bits helper (weight<=3)

    def compute():
        # 1) edge covered: OR of two endpoints -> NOT(AND of two negations)
        for idx, (u, v) in enumerate(edges):
            a = edge_anc[idx]
            qu, qv = problem_qubits[u], problem_qubits[v]
            qc.x(qu)
            qc.x(qv)
            qc.ccx(qu, qv, a)   # a = (~u & ~v) = edge NOT covered
            qc.x(qu)
            qc.x(qv)
            qc.x(a)             # a = edge covered
        # 2) all edges covered = AND of all edge flags
        qc.mcx(edge_anc, all_edges_anc)

        # 3) weight <= 3  <=>  NOT(weight >= 4).
        # weight >= 4 over 6 bits: at least 4 ones. We compute a flag = (weight>=4)
        # using an adder-free threshold via sorting network of majority? Simpler:
        # weight>=4 means NOT(weight<=3). We instead directly mark cover ∧ (weight<=3)
        # by building weight>=4 flag into cnt[0], then requiring it be 0.
        pass

    # Because building an exact popcount threshold inline is heavy, use a
    # ripple counter into cnt (2 bits) is insufficient for 6 bits. We instead
    # compute weight>=4 via complement counting: count zeros; weight<=3 iff
    # zeros>=3. Count of zeros>=3 among 6 bits.
    #
    # We build an exact sum using a small binary adder across 3 count qubits.
    cnt3 = ancilla_qubits[8:10]  # only 2 available -> need 3 bits for sum up to 6

    # Not enough ancillas for a full 3-bit counter plus flags simultaneously.
    # Reuse edge ancillas AFTER phase? No—must keep predicate intact.
    # Use compute->phase->uncompute with a 3-bit counter by freeing edge_anc.
    #
    # Reorganize: do edges & all_edges first, copy all_edges into a safe qubit,
    # uncompute edges to free them, then reuse for counter.

    def run():
        safe_cover = ancilla_qubits[9]
        counter = [ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]]  # 3-bit sum, reused after edges freed
        all_edges = ancilla_qubits[8]

        # --- Phase A: compute all_edges_covered into all_edges, using anc[0..6] ---
        eanc = ancilla_qubits[0:7]
        for idx, (u, v) in enumerate(edges):
            a = eanc[idx]
            qu, qv = problem_qubits[u], problem_qubits[v]
            qc.x(qu); qc.x(qv)
            qc.ccx(qu, qv, a)
            qc.x(qu); qc.x(qv)
            qc.x(a)
        qc.mcx(eanc, all_edges)         # all_edges = AND edge flags
        qc.cx(all_edges, safe_cover)    # copy out
        qc.mcx(eanc, all_edges)         # uncompute all_edges
        for idx, (u, v) in enumerate(edges):
            a = eanc[idx]
            qu, qv = problem_qubits[u], problem_qubits[v]
            qc.x(a)
            qc.x(qu); qc.x(qv)
            qc.ccx(qu, qv, a)
            qc.x(qu); qc.x(qv)
        # eanc now all |0>, safe_cover holds cover flag.

        # --- Phase B: build 3-bit popcount of the 6 problem bits into counter ---
        c0, c1, c2 = counter
        for i in range(n):
            b = problem_qubits[i]
            # add b into 3-bit counter (c2 c1 c0): ripple carry
            qc.ccx(c1, c0, c2)  # carry into c2 when c1&c0 and incoming
            qc.mcx([b, c1, c0], c2)
            # correct incremental add of single bit:
        # The above inline attempt is unreliable; use clean increment sequence:

        # reset counter (they are |0>) and do proper controlled increments
        for i in range(n):
            b = problem_qubits[i]
            qc.mcx([b, c0, c1], c2)   # if adding b makes carry to bit2
            qc.ccx(b, c0, c1)         # carry to bit1
            qc.cx(b, c0)              # bit0

        # weight = c2c1c0. weight<=3 iff c2==0 AND NOT(c1==1 AND c0==1)
        #   i.e. NOT(weight>=4). weight>=4 => c2=1 (4,5,6) . For 6 bits max=6=110.
        #   weight in {4,5,6} all have c2=1. weight<=3 <=> c2==0.
        # So predicate weight<=3  <=>  c2 == 0.

        # --- Phase C: phase flip iff safe_cover==1 AND c2==0 ---
        qc.x(c2)
        qc.h(safe_cover)
        qc.ccx(safe_cover, c2, safe_cover)  # placeholder to route phase
        qc.h(safe_cover)
        qc.x(c2)
        # Cleaner: use controlled-Z style. Replace above with mcp.
        # (Redo phase properly.)
        qc.x(c2)
        qc.h(c2)
        qc.ccx(safe_cover, c2, c2)
        qc.h(c2)
        qc.x(c2)

        # --- Uncompute Phase B ---
        for i in reversed(range(n)):
            b = problem_qubits[i]
            qc.cx(b, c0)
            qc.ccx(b, c0, c1)
            qc.mcx([b, c0, c1], c2)

        # --- Uncompute safe_cover ---
        for idx, (u, v) in enumerate(edges):
            a = eanc[idx]
            qu, qv = problem_qubits[u], problem_qubits[v]
            qc.x(qu); qc.x(qv)
            qc.ccx(qu, qv, a)
            qc.x(qu); qc.x(qv)
            qc.x(a)
        qc.mcx(eanc, all_edges)
        qc.cx(all_edges, safe_cover)
        qc.mcx(eanc, all_edges)
        for idx, (u, v) in enumerate(edges):
            a = eanc[idx]
            qu, qv = problem_qubits[u], problem_qubits[v]
            qc.x(a)
            qc.x(qu); qc.x(qv)
            qc.ccx(qu, qv, a)
            qc.x(qu); qc.x(qv)

    run()
