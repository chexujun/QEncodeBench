from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    v = problem_qubits
    e0, e1, e2, e3 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3]
    csize = ancilla_qubits[4]   # marks Hamming weight <= 2
    target = ancilla_qubits[5]  # final predicate

    # ---- compute edge-cover flags: e = OR(u, v) = NOT(AND(NOT u, NOT v)) ----
    # edge (0,1)
    qc.x(v[0]); qc.x(v[1])
    qc.ccx(v[0], v[1], e0)
    qc.x(e0)
    qc.x(v[0]); qc.x(v[1])
    # edge (1,2)
    qc.x(v[1]); qc.x(v[2])
    qc.ccx(v[1], v[2], e1)
    qc.x(e1)
    qc.x(v[1]); qc.x(v[2])
    # edge (1,3)
    qc.x(v[1]); qc.x(v[3])
    qc.ccx(v[1], v[3], e2)
    qc.x(e2)
    qc.x(v[1]); qc.x(v[3])

    # e3 = AND of all edge flags (all edges covered)
    qc.mcx([e0, e1, e2], e3)

    # ---- compute size-constraint flag: csize = 1 iff popcount(v) <= 2 ----
    # popcount(v) <= 2  <=>  NOT(popcount(v) >= 3)
    # popcount >= 3 over 4 bits: exists a set of >=3 ones.
    # There are C(4,3)=4 triples plus the all-4 case (covered by any triple).
    # popcount>=3 iff at least one of the four 3-subsets is all-ones.
    # We compute csize = 1 iff NONE of the triples is all-ones, i.e. popcount<=2.
    # Use e-flags are busy; reuse target region? We only have csize free here.
    # Compute "ge3" into csize first via OR of the four triple-ANDs, then invert.
    t = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
    # OR accumulation: csize starts 0; for each triple set csize=1 if triple all ones.
    # csize_new = csize OR (a&b&c). Implement via controlled logic without extra ancilla:
    # Use the identity: apply mcx(triple -> csize) toggles csize when triple all-ones.
    # Since at most... multiple triples can be all-ones simultaneously (popcount>=3
    # makes >=1 triple; popcount==4 makes all 4 triples). Toggling would XOR, not OR.
    # popcount==3 -> exactly 1 triple true -> csize=1. popcount==4 -> 4 triples true
    # -> XOR = 0, WRONG. So handle weight-4 separately.
    for a, b, c in t:
        qc.mcx([v[a], v[b], v[c]], csize)
    # Now csize = (#all-one-triples) mod 2 = 1 for popcount==3, 0 for popcount==4.
    # Fix popcount==4: toggle csize so it becomes 1 for popcount>=3.
    qc.mcx([v[0], v[1], v[2], v[3]], csize)
    # csize now = 1 iff popcount>=3 (3 ->1, 4 -> 0 XOR 1 =1). Invert for "<=2".
    qc.x(csize)
    # csize = 1 iff popcount <= 2.

    # ---- final predicate: target = e3 AND csize ----
    qc.ccx(e3, csize, target)
    qc.z(target)
    qc.ccx(e3, csize, target)

    # ---- uncompute csize ----
    qc.x(csize)
    qc.mcx([v[0], v[1], v[2], v[3]], csize)
    for a, b, c in reversed(t):
        qc.mcx([v[a], v[b], v[c]], csize)

    # ---- uncompute e3 ----
    qc.mcx([e0, e1, e2], e3)

    # ---- uncompute edge flags ----
    qc.x(v[1]); qc.x(v[3])
    qc.x(e2)
    qc.ccx(v[1], v[3], e2)
    qc.x(v[1]); qc.x(v[3])

    qc.x(v[1]); qc.x(v[2])
    qc.x(e1)
    qc.ccx(v[1], v[2], e1)
    qc.x(v[1]); qc.x(v[2])

    qc.x(v[0]); qc.x(v[1])
    qc.x(e0)
    qc.ccx(v[0], v[1], e0)
    qc.x(v[0]); qc.x(v[1])
