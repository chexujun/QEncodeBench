import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 2), (0, 3), (1, 3), (1, 5), (2, 3), (3, 4), (3, 5), (4, 5)]
    n = 6
    k = 3
    v = [problem_qubits[i] for i in range(n)]

    # Ancilla layout:
    #  8 edge-flag ancillas (one per edge), reused as the "all edges covered" AND target.
    #  We instead compute edge coverage flags, AND them into one flag.
    edge_flags = ancilla_qubits[0:8]      # 8 ancillas, one per edge
    cover_ok = ancilla_qubits[8]          # 1 ancilla: all edges covered
    # remaining ancillas for popcount/threshold
    cnt = ancilla_qubits[9:11]            # 2 ancillas for counting bits (weight <= 3)

    # ---- compute edge flags: flag_e = 1 iff edge e is covered (u OR v) ----
    def compute_edges():
        for e, (a, b) in enumerate(edges):
            f = edge_flags[e]
            # OR(a,b) into f (f starts at 0): f = a OR b = NOT( (NOT a) AND (NOT b) )
            qc.x(v[a]); qc.x(v[b])
            qc.x(f)
            qc.ccx(v[a], v[b], f)
            qc.x(v[a]); qc.x(v[b])

    def uncompute_edges():
        for e in reversed(range(len(edges))):
            a, b = edges[e]
            f = edge_flags[e]
            qc.x(v[a]); qc.x(v[b])
            qc.ccx(v[a], v[b], f)
            qc.x(f)
            qc.x(v[a]); qc.x(v[b])

    # ---- weight-<=3 predicate via arithmetic-free approach ----
    # We need "popcount(x) <= 3". Equivalent: NOT( popcount >= 4 ).
    # Build a 3-bit binary counter of the 6 input bits into cnt (2 bits) + carry.
    # Simpler robust route: compute sum of 6 bits into a 3-bit register using
    # a ripple of full/half adders. We have limited ancillas, so we reuse a
    # small counter register S (3 bits). We only have cnt (2 ancillas) + we can
    # borrow cover_ok temporarily? No—cover_ok holds AND result. Instead use
    # a dedicated 3-bit counter from remaining ancillas is not enough (only 2).
    #
    # Alternative: popcount<=3 over 6 bits. Note weight in {0..6}. weight>=4
    # means the count MSB pattern. We build sum S (values 0..6 need 3 bits).
    # We have exactly cnt=2 ancillas free plus we can use edge_flags AFTER
    # uncompute? They must be clean for phase. So do phase while everything set.
    #
    # Strategy: do all as nested compute. Order:
    #   compute edges -> AND into cover_ok
    #   compute weight bits S (3 bits) using 3 ancillas
    #   phase controlled on (cover_ok AND (S<=3))
    #   uncompute weight -> uncompute cover_ok -> uncompute edges
    #
    # We need 3 counter ancillas. Total used: 8 (edges) + 1 (cover_ok) = 9,
    # leaving ancillas[9],[10] = 2. Not enough for 3-bit counter.
    #
    # Free the edge_flags before counting: AND them into cover_ok, then
    # UNCOMPUTE edges immediately (cover_ok retains the value). This frees all
    # 8 edge ancillas for the counter.

    compute_edges()
    # AND all 8 edge flags into cover_ok
    qc.mcx(edge_flags, cover_ok)
    uncompute_edges()
    # now edge_flags all |0>, cover_ok = (all edges covered)

    # 3-bit counter S = s0 (LSB), s1, s2 using three freed ancillas
    s0, s1, s2 = edge_flags[0], edge_flags[1], edge_flags[2]

    def add_bit(bit):
        # S += bit, S is 3-bit (s0,s1,s2). Ripple carry with controls.
        # carry chain: new carry into s1 = s0 & bit ; into s2 = s1 & (s0&bit)
        qc.ccx(s1, s0, s2)   # if s1 and s0 both 1 and incoming... handled below
        # Proper increment-by-bit:
        # We implement: if bit: increment S.
        # increment (controlled by bit): s2 ^= s1&s0&bit ; s1 ^= s0&bit ; s0 ^= bit
        pass

    # Undo the stray gate above and implement clean controlled increment.
    qc.ccx(s1, s0, s2)  # cancels the stray ccx (self-inverse), net zero

    def inc(bit):
        # controlled (by bit) increment of 3-bit S=(s0,s1,s2), LSB s0
        qc.mcx([bit, s0, s1], s2)
        qc.ccx(bit, s0, s1)
        qc.cx(bit, s0)

    def uninc(bit):
        qc.cx(bit, s0)
        qc.ccx(bit, s0, s1)
        qc.mcx([bit, s0, s1], s2)

    for i in range(n):
        inc(v[i])

    # S now holds popcount in {0..6}. Condition weight<=3.
    # weight<=3  <=>  NOT(weight>=4).
    # weight>=4 : values 4,5,6 -> binary s2 s1 s0: 4=100,5=101,6=110.
    # So weight>=4  <=>  s2==1 AND NOT(s2 s1 s0 == 7). Since max is 6, s2=1
    # covers {4,5,6,7} but 7 impossible, so weight>=4  <=> s2 == 1.
    # Therefore weight<=3  <=>  s2 == 0.
    #
    # Phase -1 iff cover_ok AND (s2 == 0).
    qc.x(s2)
    qc.cz(cover_ok, s2)
    qc.x(s2)

    # uncompute counter
    for i in reversed(range(n)):
        uninc(v[i])

    # uncompute cover_ok
    compute_edges()
    qc.mcx(edge_flags, cover_ok)
    uncompute_edges()
