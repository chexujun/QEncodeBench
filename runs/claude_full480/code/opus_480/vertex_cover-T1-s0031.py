from qiskit import QuantumCircuit
from math import pi

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    v = problem_qubits
    edge_anc = ancilla_qubits[0:4]   # one ancilla per edge (OR of endpoints)
    count_anc = ancilla_qubits[4:6]  # 2-bit popcount accumulator (max count 4 needs 3 bits, but <=2 check uses carry)
    size_anc = ancilla_qubits[6]     # flags size <= 2
    edges = [(0, 1), (0, 3), (1, 2), (2, 3)]

    # ---- compute: edge covered ancillas (OR = NOT(AND of NOT endpoints)) ----
    for idx, (a, b) in enumerate(edges):
        e = edge_anc[idx]
        # e = va OR vb  ->  e = 1 - (1-va)(1-vb)
        qc.x(v[a]); qc.x(v[b])
        qc.x(e)
        qc.ccx(v[a], v[b], e)   # e = 1 XOR (NOT va AND NOT vb) = va OR vb
        qc.x(v[a]); qc.x(v[b])

    # ---- compute popcount of the 4 vertex bits into a 3-bit register ----
    # We need bits: c0,c1,c2 with count = c0 + 2 c1 + 4 c2. size<=2 iff c2==0 and not(count in {3,4}).
    # Use count_anc[0]=c0 (parity), count_anc[1]=c1, size_anc temporarily as c2.
    c0 = count_anc[0]
    c1 = count_anc[1]
    c2 = size_anc
    # ripple add each vertex bit
    for q in v:
        # add 1*q to (c2 c1 c0): carry chain
        # new c1 gets carry from c0&q; new c2 gets carry from c1&(c0&q)
        qc.ccx(c1, c0, c2)      # if adding will carry through c1 too? do MSB carry first
        # Actually do carries from high to low to avoid clobber:
        qc.ccx(c1, c0, c2)      # undo (placeholder) -- replaced below
        break
    # The above naive loop is fragile; implement explicit adder instead.

    # Undo the stray ccx pair (they cancel) -- ensure clean state:
    # (the two ccx above are identical and cancel, leaving c2 unchanged)

    # Explicit sequential incrementer for each of the 4 bits:
    for q in v:
        # increment 3-bit counter (c2 c1 c0) by q, MSB-first carry propagation
        qc.ccx(c1, c0, c2)  # carry into c2 when both c1,c0 set AND q -> need q too
        qc.ccx(c1, c0, c2)  # cancel; real logic below
        # real: controlled by q
        qc.mcx([q, c1, c0], c2)   # c2 ^= q & c1 & c0
        qc.ccx(q, c0, c1)         # c1 ^= q & c0
        qc.cx(q, c0)              # c0 ^= q

    # Now count = c0 + 2 c1 + 4 c2. size<=2  iff  NOT(c2) AND NOT(c1 AND c0)
    # i.e. size>2 (3 or 4) iff c2==1 OR (c1==1 AND c0==1).
    # Build size_ok flag on an ancilla? We reuse: we already used size_anc as c2.
    # Need a separate flag. Use edge_anc are occupied. Instead fold size condition
    # directly into the final multi-control phase.

    # ---- phase: mark iff all edges covered AND size<=2 ----
    # all edges covered: edge_anc all ==1.
    # size<=2: c2==0 and not(c1 and c0).
    # Represent "size ok" as controls: c2==0 (control on |0>) and not both c1,c0.
    # Handle the two size-bad sub-cases by subtracting, but phase oracle needs
    # exact marking. Use the identity:
    #   mark = AllEdges AND (¬c2) AND ¬(c1 ∧ c0)
    #        = AllEdges AND ¬c2 AND (¬c1 ∨ ¬c0)
    # Apply phase for AllEdges∧¬c2∧¬c1  plus  AllEdges∧¬c2∧c1∧¬c0 ... overlaps.
    # Cleaner: temporarily compute a single flag using c0 region freed order.
    # Compute t = (c1 AND c0) into a spare: no spare left, so use ¬c2 gating with
    # decomposition into two disjoint terms:
    #   term A: ¬c2 ∧ ¬c1                (counts 0,1 and 4? no, c2=0 so 0 or 1)
    #   term B: ¬c2 ∧  c1 ∧ ¬c0          (count 2)
    # A∪B are disjoint and equal size<=2 with c2=0. 
    ctrls_edges = list(edge_anc)

    # term A: edges all 1, c2=0, c1=0  -> phase
    qc.x(c2); qc.x(c1)
    qc.mcp(pi, ctrls_edges + [c2, c1], v[0] if False else edge_anc[0])  # placeholder guard
    qc.x(c1); qc.x(c2)

    # The mcp above is malformed; do proper mcp with a target being last control via mcp semantics.
    # mcp applies phase controlled on all listed qubits being 1; last arg is the "target" but
    # for phase it's symmetric. Redo cleanly below and cancel the malformed one.
    qc.x(c2); qc.x(c1)
    qc.mcp(pi, ctrls_edges + [c2, c1], edge_anc[0])
    qc.x(c1); qc.x(c2)

    # Proper phase terms using mcp(angle, control_qubits_except_last, target):
    # In Qiskit mcp(lam, controls, target) phases |1...1> of controls+target.
    # Term A controls-set S_A = edges ∪ {c2=0,c1=0}: flip c2,c1 to controls.
    def phase_all(qubits):
        qc.mcp(pi, qubits[:-1], qubits[-1])

    # Term A
    qc.x(c2); qc.x(c1)
    phase_all(ctrls_edges + [c2, c1])
    qc.x(c1); qc.x(c2)
    # Term B
    qc.x(c2); qc.x(c0)
    phase_all(ctrls_edges + [c2, c0, c1])
    qc.x(c0); qc.x(c2)

    # ---- uncompute popcount (mirror, reverse order) ----
    for q in reversed(v):
        qc.cx(q, c0)
        qc.ccx(q, c0, c1)
        qc.mcx([q, c1, c0], c2)
        qc.ccx(c1, c0, c2)
        qc.ccx(c1, c0, c2)

    # ---- uncompute edge ancillas ----
    for idx, (a, b) in enumerate(edges):
        e = edge_anc[idx]
        qc.x(v[a]); qc.x(v[b])
        qc.ccx(v[a], v[b], e)
        qc.x(e)
        qc.x(v[a]); qc.x(v[b])
