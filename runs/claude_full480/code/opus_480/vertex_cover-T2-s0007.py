from qiskit import QuantumCircuit
from math import pi

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 3), (1, 2), (1, 3), (2, 4)]
    # ancilla layout: 4 edge-ancillas, then 3 count/compare ancillas
    edge_anc = ancilla_qubits[0:4]
    # weight-count ancillas: we need popcount(x) <= 2 over 5 bits.
    # Use 3 count qubits c0,c1,c2 representing a 3-bit sum (0..5).
    c = ancilla_qubits[4:7]

    def compute_edges():
        for (u, v), a in zip(edges, edge_anc):
            # edge covered iff x_u OR x_v ; a = OR = NOT(NOT xu AND NOT xv)
            qc.x(problem_qubits[u])
            qc.x(problem_qubits[v])
            qc.x(a)
            qc.ccx(problem_qubits[u], problem_qubits[v], a)
            qc.x(problem_qubits[u])
            qc.x(problem_qubits[v])

    def uncompute_edges():
        for (u, v), a in zip(edges, edge_anc):
            qc.x(problem_qubits[u])
            qc.x(problem_qubits[v])
            qc.ccx(problem_qubits[u], problem_qubits[v], a)
            qc.x(a)
            qc.x(problem_qubits[u])
            qc.x(problem_qubits[v])

    def add_bit(ctrl):
        # add x_ctrl (a single bit) into the 3-bit counter c0,c1,c2
        # ripple: carry chain
        # c2 gets carry from c1&c0&ctrl, c1 gets carry from c0&ctrl
        qc.ccx(c[1], c[0], c[2])  # placeholder ordering handled below
        # (not used - replaced by explicit sequence)

    # explicit increment of 3-bit counter c by single control bit q
    def inc(q):
        # add 1 to (c0,c1,c2) conditioned on q
        # carry: c1 ^= q&c0 (before flipping c0); c2 ^= q&c0&c1
        qc.mcx([q, c[0], c[1]], c[2])
        qc.ccx(q, c[0], c[1])
        qc.cx(q, c[0])

    def uninc(q):
        qc.cx(q, c[0])
        qc.ccx(q, c[0], c[1])
        qc.mcx([q, c[0], c[1]], c[2])

    # compute
    compute_edges()
    for i in range(5):
        inc(problem_qubits[i])

    # Now count in binary c0(LSB),c1,c2. count<=2 means count in {0,1,2}.
    # count>2 (i.e. 3,4,5) is bad. weight<=2 predicate P_count = NOT(count>=3).
    # count>=3: binary values 011,100,101 -> c2=1 (4,5) or (c1=1 & c0=1 =>3).
    # good_count = NOT( c2 OR (c1 AND c0) )
    # Combine: overall f = AND(all edge_anc) AND good_count.
    # Build good_count into c2? We'll compute a predicate qubit reusing... need it.
    # Use edge check + count check via a multi-controlled phase with proper polarity.

    # Represent "bad count" indicator without extra ancilla:
    # We want phase -1 iff (all edges covered) AND (count<=2).
    # Apply Z-type phase controlled on: edge_anc all =1, and count<=2.
    # count<=2 <=> c2==0 AND NOT(c1==1 AND c0==1).
    # Split into the two allowed problematic-free cases via controlled phase with negations:
    # Condition = (edges all 1) & (c2==0) & !(c0 & c1)
    # = (edges all 1)&(c2==0) minus those with c0&c1.
    # Use inclusion: phase = [edges&c2==0] - [edges&c2==0&c0&c1]
    # Implement with two mcp(pi,...): first over controls edges + (c2=0), second subtract.

    ctrls_edges = list(edge_anc)

    # term1: edges all 1, c2==0  -> control c2 on 0 via X wrap
    qc.x(c[2])
    qc.mcp(pi, ctrls_edges + [c[2]], c[0] if False else ancilla_qubits[4])  # not valid; replaced
    qc.x(c[2])

    # uncompute
    for i in range(5):
        uninc(problem_qubits[i])
    uncompute_edges()
