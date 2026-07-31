import math
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    v = problem_qubits
    edges = [(0, 1), (0, 2), (0, 4), (1, 2), (1, 4), (2, 3), (2, 5), (4, 5)]

    edge_anc = ancilla_qubits[0:8]      # one ancilla per edge (OR of endpoints)
    cnt_anc = ancilla_qubits[8:11]      # 3 ancillas: count of set problem qubits (0..6 needs 3 bits)
    # We need to check: all edges covered AND popcount <= 3.
    # Strategy:
    #  1. Compute each edge-cover bit into edge_anc (OR of two endpoints).
    #  2. Compute popcount<=3 predicate. popcount ranges 0..6 -> 3-bit counter c2 c1 c0.
    #     popcount<=3 means NOT(c2==1 AND (c1==1 OR c0==1))... but <=3 => value in {0,1,2,3}.
    #     3-bit value <=3 iff c2==0. So predicate_count = NOT c2.
    #  We have 3 count ancillas -> use as ripple counter bits c0,c1,c2.
    c0, c1, c2 = cnt_anc[0], cnt_anc[1], cnt_anc[2]

    # ---- compute edge OR bits: a = x_u OR x_v = NOT( (NOT x_u) AND (NOT x_v) )
    def compute_edge(a, u, w):
        qc.x(v[u]); qc.x(v[w])
        qc.ccx(v[u], v[w], a)   # a = (NOT x_u)&(NOT x_w)  after the X's -> AND of complements
        qc.x(v[u]); qc.x(v[w])
        qc.x(a)                 # a = NOT(...) = x_u OR x_w
    def uncompute_edge(a, u, w):
        qc.x(a)
        qc.x(v[u]); qc.x(v[w])
        qc.ccx(v[u], v[w], a)
        qc.x(v[u]); qc.x(v[w])

    for a, (u, w) in zip(edge_anc, edges):
        compute_edge(a, u, w)

    # ---- compute popcount into c0,c1,c2 via ripple full-adder additions of each problem qubit
    # Add each v[i] (a single bit) to the 3-bit counter (c2 c1 c0).
    def add_bit(b):
        # increment counter by b (b is a qubit holding 0/1)
        # carry chain: use controlled toggles. Adding one bit:
        #  new c2 ^= b & c1 & c0 ; c1 ^= b & c0 ; c0 ^= b
        # apply in order c2 then c1 then c0 to use old values
        qc.mcx([b, c1, c0], c2)
        qc.ccx(b, c0, c1)
        qc.cx(b, c0)
    def unadd_bit(b):
        qc.cx(b, c0)
        qc.ccx(b, c0, c1)
        qc.mcx([b, c1, c0], c2)

    for i in range(6):
        add_bit(v[i])

    # ---- phase: mark iff all edge_anc == 1 AND c2 == 0
    # condition = (AND of all edge_anc) AND (NOT c2)
    qc.x(c2)  # now c2 flag = 1 means count<=3
    controls = list(edge_anc) + [c2]
    # apply Z-phase controlled on all controls == 1 : use mcp(pi,...) which gives phase on all-ones
    qc.mcp(math.pi, controls[:-1], controls[-1])
    qc.x(c2)

    # ---- uncompute popcount
    for i in reversed(range(6)):
        unadd_bit(v[i])

    # ---- uncompute edges
    for a, (u, w) in zip(reversed(edge_anc), reversed(edges)):
        uncompute_edge(a, u, w)
