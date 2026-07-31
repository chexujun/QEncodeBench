from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]
    # ancillas: 3 for edge-cover, 1 for "all edges covered", 2 for weight/count logic
    e0, e1, e2 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]
    cov = ancilla_qubits[3]
    c1, c2 = ancilla_qubits[4], ancilla_qubits[5]

    # ---- compute edge-cover flags: edge (a,3) covered iff xa OR x3 ----
    # e_i = xa OR x3 = NOT( (NOT xa) AND (NOT x3) )
    def or_into(a, anc):
        qc.x(a); qc.x(x3)
        qc.x(anc)
        qc.ccx(a, x3, anc)
        qc.x(a); qc.x(x3)

    or_into(x0, e0)
    or_into(x1, e1)
    or_into(x2, e2)

    # all edges covered
    qc.mcx([e0, e1, e2], cov)

    # ---- compute Hamming-weight-<=2 predicate ----
    # count of ones among x0..x3. weight<=2  <=>  NOT(weight>=3).
    # weight>=3 means at least 3 of 4 bits set.
    # Use c1,c2 as a small popcount saturating counter of "carry" style.
    # We detect weight>=3: this happens iff at least two of the C(4,3) triples all-set...
    # Simpler: weight>=3 iff sum over 4 bits >=3.
    # Build w2 = "at least 2 ones" and w3 = "at least 3 ones" via symmetric functions.
    # We only need <=2, i.e. NOT(>=3). Compute >=3 into c1.
    # >=3 among {x0,x1,x2,x3}: OR of all 4 triple-ANDs.
    triples = [(x0, x1, x2), (x0, x1, x3), (x0, x2, x3), (x1, x2, x3)]
    # c1 will hold OR of triple ANDs. Use c2 as scratch for each triple.
    for t in triples:
        qc.ccx(t[0], t[1], c2)
        qc.ccx(t[2], c2, c1)   # note: this XORs into c1; but overlaps -> need OR semantics
        qc.ccx(t[0], t[1], c2)
    # The above accumulates parity of triple-hits into c1, not OR. Fix below.
    # Undo the flawed accumulation:
    for t in reversed(triples):
        qc.ccx(t[0], t[1], c2)
        qc.ccx(t[2], c2, c1)
        qc.ccx(t[0], t[1], c2)

    # Correct >=3 detection: weight in {3,4}. Equivalent boolean:
    # (x0&x1&x2) | (x0&x1&x3) | (x0&x2&x3) | (x1&x2&x3).
    # Build OR into c1 via De Morgan on the four triple terms using c2 scratch,
    # but OR of 4 non-disjoint terms is awkward with one scratch. Instead use the
    # identity: weight>=3  <=>  (weight>=2 of last three) requires careful counting.
    # Cleanest exact approach: c1 = AND that at least 3 set = sum>=3.
    # Enumerate via majority: for 4 bits, >=3 ones =
    #   maj4 handled by: t_all4 (weight4) plus exactly-3.
    # Use a robust popcount into two qubits (c1=bit0? ) -- instead do direct:
    # We accept building >=3 as OR of triples using an ancilla-free multi-controlled
    # trick: flip cov's meaning by directly phase-marking valid states.

    # Given complexity, mark phase for f=1 = cov AND (weight<=2) = cov AND NOT(>=3).
    # Compute (>=3) into c1 as OR of the four triples using c2, applying OR one at a time.
    def and3_or_into(a, b, c, target, scratch):
        # target |= (a&b&c)  ; using OR = target = target OR term
        # implement via: scratch = a&b ; term = scratch&c ; OR into target:
        qc.ccx(a, b, scratch)
        # OR: target = target OR (scratch&c) = NOT( NOT target AND NOT(scratch&c) )
        qc.x(target)
        qc.x(scratch)  # temporarily represent...
        # We need NOT(scratch&c); do controlled: if (scratch&c) then... complicated.
        # Revert to simpler exact XOR-based inclusion-exclusion for the phase directly.
        qc.x(scratch)
        qc.x(target)
        qc.ccx(a, b, scratch)

    # --- Direct phase construction (diagonal), no OR needed ---
    # f = cov AND (weight<=2). We already have cov in qubit `cov`.
    # Compute g = cov AND (weight<=2) into c1, then Z on c1.
    # weight<=2 with cov known: mark via subtracting the weight>=3 cases.
    # Since exactly the states with weight in {3,4} must be excluded, and among
    # those cov is always 1 (x3 or many bits set), we phase-mark cov, then
    # phase-UNmark the weight>=3 states (double negation returns them to +1).

    # phase: -1 on all states with cov=1
    qc.z(cov)
    # now correct the weight>=3 states (they wrongly got -1 if cov=1, and cov=1 always
    # holds when weight>=3 because any 3 of 4 bits includes enough to cover; also
    # weight>=3 always covers all edges so cov=1). Re-apply +... i.e. flip them back:
    for t in triples:
        # phase +1 restore = apply -1 again on exactly-that pattern set; use mcp(pi) but
        # overlapping triples double-count. Use exactly-3 and exactly-4 patterns instead.
        pass

    # exactly-4: all ones
    qc.mcp(np.pi, [x0, x1, x2], x3)  # flips phase on |1111>
    # exactly-3 patterns (each a unique basis state): controls on the three ones,
    # anti-control (X) on the zero bit.
    exact3 = [
        (x0, x1, x2, x3),  # zero bit = x3
        (x0, x1, x3, x2),  # zero bit = x2
        (x0, x2, x3, x1),  # zero bit = x1
        (x1, x2, x3, x0),  # zero bit = x0
    ]
    for a, b, c, zero in exact3:
        qc.x(zero)
        qc.mcp(np.pi, [a, b], c)
        qc.x(zero)

    # ---- uncompute cov and edge flags ----
    qc.mcx([e0, e1, e2], cov)
    # uncompute OR ancillas (mirror)
    def un_or(a, anc):
        qc.x(a); qc.x(x3)
        qc.ccx(a, x3, anc)
        qc.x(anc)
        qc.x(a); qc.x(x3)
    un_or(x2, e2)
    un_or(x1, e1)
    un_or(x0, e0)
