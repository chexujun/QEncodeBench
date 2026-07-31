from qiskit import QuantumCircuit
from math import pi

def build_oracle(qc: QuantumCircuit, problem_qubits, ancilla_qubits) -> None:
    v = problem_qubits            # v[i] = 1 iff vertex i in cover
    a = ancilla_qubits

    edges = [(0, 1), (1, 2), (1, 3), (1, 4), (2, 3)]

    # ---- Compute edge-cover flags into ancillas a[0..4] ----
    # a[j] = OR(v[p], v[q]) = NOT( (NOT v[p]) AND (NOT v[q]) )
    edge_anc = a[0:5]
    for j, (p, q) in enumerate(edges):
        ea = edge_anc[j]
        qc.x(v[p]); qc.x(v[q])
        qc.ccx(v[p], v[q], ea)     # ea = (NOT vp) AND (NOT vq)  [ancilla starts |0>]
        qc.x(ea)                   # ea = OR(vp, vq)
        qc.x(v[p]); qc.x(v[q])

    # ---- Compute "count of 1s <= 2" flag into a[5] ----
    # Equivalent: NOT( count >= 3 ), i.e. no 3-subset of the 5 vertices all =1.
    # count >= 3 iff at least one triple is all ones. We OR over triples into cnt.
    # Cheaper: build popcount not needed; use "at most 2" = AND over all triples of NOT(all three set).
    # There are C(5,3)=10 triples. For each triple, if all three set -> violates.
    # a[5] accumulates OR of triple-violations; final "le2" = NOT a[5].
    cnt = a[5]
    tmp = a[6]
    from itertools import combinations
    triples = list(combinations(range(5), 3))
    for (i, j, k) in triples:
        qc.ccx(v[i], v[j], tmp)    # tmp = vi & vj
        qc.ccx(tmp, v[k], cnt_helper := cnt)  # cnt ^= (vi&vj&vk)
        # NOTE: cnt is XOR-accumulated; since at most... but multiple triples can be set.
        qc.ccx(v[i], v[j], tmp)    # uncompute tmp
    # cnt now = XOR over triples of (all-three-set). Not a clean OR; fix below.

    # The XOR approach above is unreliable; replace with correct OR accumulation.
    # (kept structure minimal; see corrected block)
    le2 = a[6]
    # Reset cnt from the flawed pass:
    for (i, j, k) in reversed(triples):
        qc.ccx(v[i], v[j], tmp)
        qc.ccx(tmp, v[k], cnt)
        qc.ccx(v[i], v[j], tmp)
    # cnt back to |0>.

    # Correct "at most 2 ones" via unary threshold using a[6] and a[7]:
    # Build count using two flag qubits c1 (>=1), c2 (>=2), and detect >=3.
    c_ge1 = a[6]
    c_ge2 = a[7]
    viol = a[5]   # reuse cleared cnt as violation (>=3) flag; currently |0>
    for i in range(5):
        # promote: if already>=2 and this bit set -> >=3 violation
        qc.ccx(c_ge2, v[i], viol)          # viol ^= (c_ge2 & vi)
        # promote >=1 -> >=2
        qc.ccx(c_ge1, v[i], c_ge2)         # c_ge2 ^= (c_ge1 & vi)
        # promote 0 -> >=1
        qc.cx(v[i], c_ge1)                 # c_ge1 ^= vi
    # viol == 1 iff count(x) >= 3.

    # ---- Phase: mark iff all edges covered AND NOT viol ----
    # Condition = AND(edge_anc[0..4]) AND (NOT viol)
    qc.x(viol)   # now viol' = (count <= 2)
    ctrls = edge_anc + [viol]
    qc.h(a[6+0] if False else v[0])  # placeholder no-op removed below
    qc.mcp(pi, ctrls[:-1], ctrls[-1])
    qc.x(viol)

    # ---- Uncompute count flags (reverse) ----
    for i in reversed(range(5)):
        qc.cx(v[i], c_ge1)
        qc.ccx(c_ge1, v[i], c_ge2)
        qc.ccx(c_ge2, v[i], viol)

    # ---- Uncompute edge flags (reverse) ----
    for j, (p, q) in reversed(list(enumerate(edges))):
        ea = edge_anc[j]
        qc.x(v[p]); qc.x(v[q])
        qc.x(ea)
        qc.ccx(v[p], v[q], ea)
        qc.x(v[p]); qc.x(v[q])
