import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 2), (0, 5), (1, 2), (1, 4), (1, 5), (2, 4), (3, 4), (4, 5)]
    n = 6
    k = 4

    edge_anc = ancilla_qubits[0:8]      # one ancilla per edge (edge covered flag)
    cnt = ancilla_qubits[8:11]          # 3-bit popcount register (max count 6 -> 3 bits)
    # We need a final "all conditions satisfied" flag; reuse edge ancillas region.
    # But all 11 ancillas are used (8 edges + 3 count). Use a phase via multi-controlled Z
    # over the 8 edge flags AND the "<=4" predicate expressed on count bits.

    # ---- compute: edge covered flags ----
    for idx, (u, v) in enumerate(edges):
        a = edge_anc[idx]
        # a = u OR v = NOT( (NOT u) AND (NOT v) )
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], a)
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.x(a)  # now a = u OR v

    # ---- compute: popcount of the 6 problem qubits into 3-bit register cnt ----
    def add_one(control):
        # increment 3-bit counter cnt (cnt[0] LSB) controlled on `control`
        # carry chain: bit2 ^= control & c0 & c1 ; bit1 ^= control & c0 ; bit0 ^= control
        qc.mcx([control, cnt[0], cnt[1]], cnt[2])
        qc.ccx(control, cnt[0], cnt[1])
        qc.cx(control, cnt[0])

    for i in range(n):
        add_one(problem_qubits[i])

    # ---- predicate: count <= 4  i.e. NOT(count >= 5) ----
    # count in [0..6], 3 bits: value = cnt2*4 + cnt1*2 + cnt0
    # count >= 5 means (cnt2 AND cnt1) [6=110,7 unused] OR (cnt2 AND cnt0) [5=101].
    # count <= 4  <=>  NOT cnt2  OR  (NOT cnt1 AND NOT cnt0)
    #            <=>  NOT( cnt2 AND (cnt1 OR cnt0) )
    # We want overall predicate P = (all 8 edges covered) AND (count <= 4).
    # Apply phase -1 when P holds. Use a controlled-Z structure:
    # Flip a marker built from: le4 flag.
    le4 = cnt[0]  # placeholder not used; we build le4 into an edge ancilla temporarily?
    # All ancillas occupied; instead fold count<=4 into phase via an mcp with X-conditioning.

    # Strategy: phase = -1 iff (all edge flags == 1) AND (count <= 4).
    # count <= 4 == NOT(cnt2 AND (cnt1 OR cnt0)).
    # Enumerate the two disallowed count-high configs and subtract them:
    # Easier: temporarily compute le4 into cnt is impossible (needed). Use last edge ancilla
    # after saving. We instead express with inclusion via multi-controlled phase directly.

    # Compute g = cnt1 OR cnt0 into a fresh scratch — none free. So compute h = cnt2 AND (cnt1 OR cnt0)
    # We can reuse an edge ancilla only after copying its value; not safe. Use direct MCP terms:
    # Apply -1 phase to states where all edges covered:
    #   term_full: mcp(pi) controlled on all 8 edge flags AND (extra conditioning making count<=4).
    # Decompose count<=4 = 1 - [cnt2 & cnt1] - [cnt2 & cnt0 & ~cnt1].
    # So phase(all_edges AND count<=4)
    #   = phase(all_edges) - phase(all_edges & cnt2 & cnt1)
    #                      - phase(all_edges & cnt2 & cnt0 & ~cnt1)
    ctrl = list(edge_anc)

    # Term A: all edges -> phase pi
    qc.mcp(math.pi, ctrl[:-1], ctrl[-1])

    # Term B: all edges & cnt2 & cnt1 -> phase -pi (cancel)
    qc.mcp(-math.pi, ctrl + [cnt[2]], cnt[1])

    # Term C: all edges & cnt2 & cnt0 & ~cnt1 -> phase -pi (cancel)
    qc.x(cnt[1])
    qc.mcp(-math.pi, ctrl + [cnt[2], cnt[1]], cnt[0])
    qc.x(cnt[1])

    # ---- uncompute popcount (reverse) ----
    def add_one_inv(control):
        qc.cx(control, cnt[0])
        qc.ccx(control, cnt[0], cnt[1])
        qc.mcx([control, cnt[0], cnt[1]], cnt[2])

    for i in reversed(range(n)):
        add_one_inv(problem_qubits[i])

    # ---- uncompute edge flags (reverse) ----
    for idx in reversed(range(len(edges))):
        u, v = edges[idx]
        a = edge_anc[idx]
        qc.x(a)
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], a)
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
