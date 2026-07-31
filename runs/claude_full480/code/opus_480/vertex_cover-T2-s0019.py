from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 1), (0, 2), (0, 4), (1, 2), (1, 3), (2, 4)]
    p = problem_qubits
    n = len(p)  # 5

    # Ancilla layout:
    #   edge_anc: one ancilla per edge that becomes 1 iff that edge is covered
    #   count ancillas: 3 qubits to hold popcount (0..5 needs 3 bits)
    #   final flag ancilla for the phase kick target combining edge-AND and count<=3
    # We have 9 ancillas total.
    edge_anc = [ancilla_qubits[i] for i in range(6)]   # 6
    cnt = [ancilla_qubits[6], ancilla_qubits[7], ancilla_qubits[8]]  # 3 count bits

    def compute():
        # ---- edge coverage: edge covered iff (x_u OR x_v) ----
        # OR via De Morgan: NOT(NOT x_u AND NOT x_v). Compute into edge_anc[i]=covered.
        for i, (u, v) in enumerate(edges):
            a = edge_anc[i]
            qc.x(p[u]); qc.x(p[v])
            qc.ccx(p[u], p[v], a)   # a = (NOT xu)AND(NOT xv) after we conceptually flip
            qc.x(p[u]); qc.x(p[v])
            qc.x(a)                 # a = NOT(that) = xu OR xv = covered
        # ---- popcount of x into cnt (3-bit ripple adder of single bits) ----
        # Add each problem bit into the 3-bit counter cnt[0]=LSB,cnt[1],cnt[2]=MSB.
        for j in range(n):
            b = p[j]
            # carry propagate: increment counter by b
            # cnt2 ^= b & cnt0 & cnt1 ; cnt1 ^= b & cnt0 ; cnt0 ^= b
            qc.mcx([b, cnt[0], cnt[1]], cnt[2])
            qc.ccx(b, cnt[0], cnt[1])
            qc.cx(b, cnt[0])

    def uncompute():
        # mirror popcount
        for j in reversed(range(n)):
            b = p[j]
            qc.cx(b, cnt[0])
            qc.ccx(b, cnt[0], cnt[1])
            qc.mcx([b, cnt[0], cnt[1]], cnt[2])
        # mirror edges
        for i, (u, v) in enumerate(edges):
            a = edge_anc[i]
            qc.x(a)
            qc.x(p[u]); qc.x(p[v])
            qc.ccx(p[u], p[v], a)
            qc.x(p[u]); qc.x(p[v])

    compute()

    # Phase condition: all edges covered (all edge_anc == 1) AND count <= 3.
    # count <= 3  <=>  NOT (count >= 4)  <=>  NOT (cnt[2]==1 AND (cnt[1] or cnt[0]))
    # For popcount over 5 bits, count in 0..5. count>=4 means bit2 set (4 or 5).
    # 4 = 100, 5 = 101. So count>=4 iff cnt[2]==1. Thus count<=3 iff cnt[2]==0.
    # Phase -1 iff (all edges covered) AND cnt[2]==0.
    # Flip cnt[2] so that the "good" (cnt[2]==0) maps to control=1.
    qc.x(cnt[2])
    controls = list(edge_anc) + [cnt[2]]
    qc.h(controls[-1])
    qc.mcx(controls[:-1], controls[-1])
    qc.h(controls[-1])
    qc.x(cnt[2])

    uncompute()
