from qiskit import QuantumCircuit
from math import pi

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    v = problem_qubits
    edges = [(0, 1), (0, 2), (0, 4), (2, 3), (3, 4)]

    # Ancilla layout:
    #   a_edges[0..4] : one ancilla per edge (edge is covered)
    #   c1, c2, c3    : 3 ancillas for counting popcount bits (count <= 2)
    a_edge = ancilla_qubits[0:5]
    c = ancilla_qubits[5:8]  # c[0],c[1],c[2] = bits of popcount (0..5 needs 3 bits)
    flag_all = ancilla_qubits[4]  # reuse note: we need distinct flag; use a_edge? No.

    # We need a final flag qubit for the phase; reuse discipline below.
    # We have 8 ancillas: 5 edges + 3 count bits = 8. Use one edge ancilla as
    # combined flag by an alternative scheme: instead accumulate everything into
    # count ancillas and edge ancillas, then MCX onto a chosen ancilla temporarily.

    # ---- COMPUTE: edge coverage ----
    # edge covered iff (v_i OR v_j). Compute NOT(covered) = (NOT v_i)AND(NOT v_j)
    # into a_edge, i.e. a_edge = 1 when edge is UNcovered.
    for idx, (i, j) in enumerate(edges):
        qc.x(v[i]); qc.x(v[j])
        qc.ccx(v[i], v[j], a_edge[idx])
        qc.x(v[i]); qc.x(v[j])
    # Now all edges covered  <=>  all a_edge == 0.

    # ---- COMPUTE: popcount of the 5 vertex bits into c[0..2] ----
    # Ripple full-adder style accumulation of 5 single bits.
    # count = sum v[i]; store 3-bit binary in c[0](LSB),c[1],c[2](MSB).
    # Add each v[i] to the counter c.
    def add_bit(bit):
        # c += bit ; carry ripple across 3 bits
        # carry from bit0
        qc.ccx(bit, c[0], c[1])         # carry into bit1 if c0&bit
        # need carry into bit2: when bit & c0 & c1
        qc.mcx([bit, c[0], c[1]], c[2]) # (before flipping c1) approximate—use ordering below

    # The naive add_bit above double-uses; implement a correct sequential adder:
    # For adding a single bit b to counter (c0,c1,c2):
    #   new c2 ^= b & c0 & c1
    #   new c1 ^= b & c0
    #   new c0 ^= b
    # Order high-to-low so lower bits still hold pre-add values.
    def add_one(b):
        qc.mcx([b, c[0], c[1]], c[2])
        qc.ccx(b, c[0], c[1])
        qc.cx(b, c[0])
    for i in range(5):
        add_one(v[i])

    # count <= 2  <=>  binary count in {0,1,2} = 000,001,010
    #   <=>  NOT( c2==1 OR (c1==1 AND c0==1) )
    # i.e. count > 2 iff c2 OR (c1 AND c0).
    # We want f=1 when: all a_edge==0  AND  count<=2.

    # ---- combine into phase ----
    # Condition for f=1:
    #   every a_edge[idx] == 0   (5 conditions)
    #   c2 == 0
    #   NOT (c1==1 AND c0==1)
    #
    # Apply a multi-controlled Z that fires only on the good subspace.
    # Turn "==0" controls into positive controls by X.
    for idx in range(5):
        qc.x(a_edge[idx])
    qc.x(c[2])
    # Handle NOT(c1 AND c0): fire unless both c1,c0 are 1.
    # Equivalent good-count condition: (c0,c1) in {00,01,10}. Combined with
    # c2==0 this exactly means count in {0,1,2}.
    # We implement mcp phase over the full good predicate by splitting the
    # (c0,c1) != 11 clause. Use the identity:
    #   phase over [A and (c0,c1)!=11] = phase[A and c1'=... ]
    # Simpler: enumerate the three allowed (c0,c1) patterns as separate MCPs,
    # each combined with the fixed A-controls (a_edge flipped, c2 flipped).
    Ctrls_base = [a_edge[0], a_edge[1], a_edge[2], a_edge[3], a_edge[4], c[2]]

    # pattern (c0,c1) = (0,0): need c0==0 and c1==0
    qc.x(c[0]); qc.x(c[1])
    qc.mcp(pi, Ctrls_base + [c[0]], c[1])
    qc.x(c[0]); qc.x(c[1])
    # pattern (c0,c1) = (1,0): c0==1, c1==0
    qc.x(c[1])
    qc.mcp(pi, Ctrls_base + [c[0]], c[1])
    qc.x(c[1])
    # pattern (c0,c1) = (0,1): c0==0, c1==1
    qc.x(c[0])
    qc.mcp(pi, Ctrls_base + [c[0]], c[1])
    qc.x(c[0])

    # ---- restore control-flip X's ----
    qc.x(c[2])
    for idx in range(5):
        qc.x(a_edge[idx])

    # ---- UNCOMPUTE popcount (mirror of add_one loop) ----
    def unadd_one(b):
        qc.cx(b, c[0])
        qc.ccx(b, c[0], c[1])
        qc.mcx([b, c[0], c[1]], c[2])
    for i in reversed(range(5)):
        unadd_one(v[i])

    # ---- UNCOMPUTE edge ancillas (mirror) ----
    for idx, (i, j) in enumerate(edges):
        qc.x(v[i]); qc.x(v[j])
        qc.ccx(v[i], v[j], a_edge[idx])
        qc.x(v[i]); qc.x(v[j])
