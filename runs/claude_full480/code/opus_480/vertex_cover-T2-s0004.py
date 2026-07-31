from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 2), (1, 2), (2, 3), (2, 4), (3, 4)]
    v = problem_qubits
    edge_anc = ancilla_qubits[0:6]
    cover_anc = ancilla_qubits[6]
    count_anc = ancilla_qubits[7:9]  # 2 qubits: count up to 5 needs 3 bits, but size<=3 check

    # --- compute edge-cover flags: edge_anc[j] = OR(v[a], v[b]) ---
    def edge_or(a, b, anc):
        # anc = a OR b = NOT( (NOT a) AND (NOT b) )
        qc.x(a); qc.x(b)
        qc.ccx(a, b, anc)   # anc = (NOT a)AND(NOT b) after we flip; but a,b flipped => anc = a'&b'
        qc.x(anc)           # anc = NOT(a'&b') = a OR b
        qc.x(a); qc.x(b)

    def edge_or_un(a, b, anc):
        qc.x(a); qc.x(b)
        qc.x(anc)
        qc.ccx(a, b, anc)
        qc.x(a); qc.x(b)

    for j, (a, b) in enumerate(edges):
        edge_or(v[a], v[b], edge_anc[j])

    # cover_anc = AND of all edge flags
    qc.mcx(edge_anc, cover_anc)

    # --- compute popcount(x) using a 3-bit counter on count register ---
    # We need size <= 3, i.e. count in {0,1,2,3}. count of 5 bits needs 3 bits.
    # We have only 2 count ancillas (count_anc) -> reuse: build predicate size<=3.
    # size<=3  <=>  NOT(size>=4)  <=> not (at least 4 of the 5 bits set).
    # "at least 4 of 5" means at most 1 zero. Enumerate: all 5 set, or exactly one zero.
    # size>=4 iff (v0&v1&v2&v3) | ... (5 terms of 4-way AND). Compute size>=4 flag.
    c4 = count_anc[0]  # flag: size >= 4
    four_sets = [
        [v[0], v[1], v[2], v[3]],
        [v[0], v[1], v[2], v[4]],
        [v[0], v[1], v[3], v[4]],
        [v[0], v[2], v[3], v[4]],
        [v[1], v[2], v[3], v[4]],
    ]
    # c4 = OR of the five 4-ANDs. These terms are mutually... not exclusive, but
    # for OR via XOR: full set (all 5) is counted in all five terms (odd=5 -> XOR ok),
    # exactly-4 counted in exactly one term. So XOR (mcx toggles) yields correct OR
    # because overlaps only at the all-5 point where multiplicity 5 is odd.
    for term in four_sets:
        qc.mcx(term, c4)

    # predicate = cover_anc AND (NOT c4). Put into count_anc[1] = result.
    res = count_anc[1]
    qc.x(c4)                      # now c4 = (size<=3)
    qc.ccx(cover_anc, c4, res)    # res = cover AND size<=3
    qc.x(c4)                      # restore c4 to (size>=4)

    # --- phase ---
    qc.z(res)

    # --- uncompute (mirror) ---
    qc.x(c4)
    qc.ccx(cover_anc, c4, res)
    qc.x(c4)

    for term in reversed(four_sets):
        qc.mcx(term, c4)

    qc.mcx(edge_anc, cover_anc)

    for j, (a, b) in enumerate(edges):
        edge_or_un(v[a], v[b], edge_anc[j])
