from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    v = problem_qubits
    edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3)]

    edge_anc = ancilla_qubits[0:5]   # one ancilla per edge (edge covered)
    cnt = ancilla_qubits[5:7]        # 2-bit popcount accumulator (count of 1-bits, capped meaning)
    result = ancilla_qubits[7]       # final predicate

    # --- compute: edge coverage ---
    # edge covered = v_a OR v_b = NOT(NOT v_a AND NOT v_b)
    for e_idx, (a, b) in enumerate(edges):
        anc = edge_anc[e_idx]
        qc.x(v[a])
        qc.x(v[b])
        qc.ccx(v[a], v[b], anc)   # anc = (NOT va)AND(NOT vb) after the X's -> anc=1 iff uncovered
        qc.x(v[a])
        qc.x(v[b])
        qc.x(anc)                 # anc = covered

    # --- compute: popcount of the 4 vertex bits into 2-bit register cnt = cnt1 cnt0 ---
    # We add each vertex bit into a 2-bit counter (max 4 -> needs 3 bits, but we only
    # need to know whether count <= 2, i.e. count in {0,1,2}; count>=3 fails).
    # Use a 2-bit saturating-style ripple add; carry-out at bit-2 signals count>=... .
    # Instead, compute full 2-bit sum with a carry ancilla borrowed from result temporarily?
    # We track an overflow flag using result qubit as temporary carry sink is unsafe; use cnt only.
    #
    # 2-bit counter add of a single bit x into (cnt1,cnt0):
    #   new carry into bit1 = cnt0 AND x ; cnt0 ^= x
    #   overflow (bit2) = cnt1 AND carry ; cnt1 ^= carry
    # We need an overflow indicator meaning count>=3 (since with <=... max useful is 3/4).
    # Detect count>=3: count>=3 iff cnt1==1 AND cnt0==1 (count==3) OR count==4 (cnt overflow).
    # To capture count==4 we OR its detection into result-based flag. Simpler: use an extra
    # carry ancilla = edge_anc is busy. We only have these ancillas; reuse none in use.
    #
    # Popcount 0..4 in 3 bits would need a 3rd bit. We lack a free ancilla (all 8 used:
    # 5 edges +2 count +1 result). But edge ancillas are still needed for phase; count not yet.
    # So borrow: do popcount BEFORE finalizing? We need both edge flags AND count at phase time.
    #
    # Resolve: fold "size<=2" as NOT(size>=3). size>=3 means at least 3 of 4 bits set.
    # Enumerate: at least 3 of {v0,v1,v2,v3}. That's OR over the 4 triples AND'd, plus the 4-set.
    # size>=3 iff (number of zero-bits <= 1) iff at most one of the bits is 0.
    # Equivalent: for the 4 pairs? Simpler exact: size>=3 = OR of the C(4,3)=4 majority-of-those-three
    # terms where each term = va AND vb AND vc.
    triples = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
    # ge3 flag stored in cnt[0]; we accumulate OR of the four AND3 terms.
    # OR accumulation: cnt0 ^= term, but overlapping terms cause double-count (XOR not OR).
    # Use controlled set: set cnt0=1 whenever a term is 1, via X-trick OR.
    # OR of terms t_i into flag: flag = 1 - prod(1 - t_i). Implement with X on flag:
    # start flag=0. For each term, do: if term==1 -> flag=1. Using mcx to set only when
    # flag currently 0 avoids nothing for phase (we just need final OR). A clean OR:
    #   flag stays 1 once set; ccx sets flag=1 if term & (not needed) -> but repeated ccx
    #   toggles. To get true OR, compute each term to a temp then OR. We have cnt[1] as temp.
    ge3 = cnt[0]
    tmp = cnt[1]
    for (a, b, c) in triples:
        # tmp = va AND vb AND vc
        qc.mcx([v[a], v[b], v[c]], tmp)
        # OR into ge3: ge3 = ge3 OR tmp  => ge3 ^= tmp AND (NOT ge3)
        qc.x(ge3)
        qc.ccx(tmp, ge3, ge3)  # invalid (control==target); replaced below
        qc.x(ge3)
        # uncompute tmp
        qc.mcx([v[a], v[b], v[c]], tmp)

    # size<=2 flag = NOT ge3
    qc.x(ge3)

    # --- phase: mark iff all edges covered AND size<=2 ---
    controls = list(edge_anc) + [ge3]
    qc.h(result)
    qc.mcx(controls, result)
    qc.h(result)
    qc.mcx(controls, result)  # uncompute result back to |0>

    # --- uncompute size<=2 flag ---
    qc.x(ge3)

    # --- uncompute ge3 OR accumulation ---
    for (a, b, c) in reversed(triples):
        qc.mcx([v[a], v[b], v[c]], tmp)
        qc.x(ge3)
        qc.ccx(tmp, ge3, ge3)
        qc.x(ge3)
        qc.mcx([v[a], v[b], v[c]], tmp)

    # --- uncompute edge coverage ---
    for e_idx, (a, b) in enumerate(edges):
        anc = edge_anc[e_idx]
        qc.x(anc)
        qc.x(v[a])
        qc.x(v[b])
        qc.ccx(v[a], v[b], anc)
        qc.x(v[a])
        qc.x(v[b])
