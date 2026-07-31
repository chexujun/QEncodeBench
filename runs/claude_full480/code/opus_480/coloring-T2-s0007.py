from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 2), (0, 4), (1, 3), (1, 4), (2, 3), (3, 4)]

    def qb(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # We have 6 edges. Ancillas: 6 edge-ancillas indicate "edge OK (colors differ)",
    # 1 spare. problem qubits = 10, ancillas = 7. Use ancilla 0..5 for edges, ancilla 6 as final.
    edge_anc = ancilla_qubits[0:6]
    final = ancilla_qubits[6]

    def color_diff_compute(u, v, anc):
        # Set anc = 1 iff decoded(color(u)) != decoded(color(v)).
        # Colors: c in {0,1,2,3} with 3==0. So decoded equal iff codes equal,
        # OR one is 00 and other is 11, OR one is 11 and other is 00.
        # i.e. decoded_equal iff (u==v) as codes, OR ({u,v}=={00,11}).
        # Let u=(a0,a1), v=(b0,b1).
        # codes equal: a0==b0 and a1==b1.
        # {00,11}: (a0==a1) and (b0==b1) and (a0 != b0)  -> one is 00 other 11.
        #   Actually 00: a0=0,a1=0 ; 11: b0=1,b1=1. Condition: a0==a1, b0==b1, a0!=b0.
        # decoded_equal = codes_equal OR pair_00_11.
        # We want anc = NOT decoded_equal = decoded_diff.
        a0, a1 = qb(u)
        b0, b1 = qb(v)

        # Compute helper flags into anc via a small routine.
        # Strategy: compute d0 = a0 XOR b0, d1 = a1 XOR b1 using two temp? We only have anc.
        # Instead compute decoded_equal directly onto anc, then X to invert.
        #
        # decoded_equal cases (enumerate the two contributing terms) but we must be reversible
        # and use only this single ancilla for the edge result. Use a scratch: reuse 'final'
        # is not safe here because compute for all edges runs before phase. So we need per-edge
        # scratch. We'll instead build decoded_diff with a compact gate net using mcx onto anc
        # for each "equal" pattern is 16 patterns -> too many.
        #
        # Better: decoded_equal == (a0==b0 AND a1==b1) OR (a0==a1 AND b0==b1 AND a0!=b0).
        # Note second term implies a0!=b0 so it's disjoint from first (first needs a0==b0).
        # So decoded_equal = T1 XOR T2 (disjoint, so OR == XOR). Great: we can XOR both onto anc.
        #
        # T1 = (a0 XNOR b0) AND (a1 XNOR b1)
        # T2 = (a0 XNOR a1) AND (b0 XNOR b1) AND (a0 XOR b0)
        #
        # Implement T1: flip a0->set so that control-on-equality. Use standard trick:
        #   put a0 XNOR b0 by: cx(b0,a0) then a0 holds a0 xor b0; XNOR = NOT that.
        # But that mutates problem qubits; we must uncompute. Instead use controlled gates with
        # X-conjugation for equality controls.
        #
        # T1: mcx controlled on (a0==b0) and (a1==b1). Equality control on pair (p,q)=1 iff p==q.
        # Realize a0==b0 control: cx(a0,b0)? mutation again. Use: control on b0 in state equal to a0
        # isn't a fixed control. So we compute parity bits into anc-adjacent? We have no spare.
        #
        # Fallback: enumerate the equal patterns for T1 and T2 directly as multi-controlled X with
        # X-conjugation (open/closed controls). decoded_equal true patterns over 4 bits (a0,a1,b0,b1):
        #   T1 (a0==b0,a1==b1): (a0,a1,b0,b1) with b0=a0,b1=a1 -> 4 patterns:
        #     0000,0101,1010,1111  (order a0,a1,b0,b1)
        #   T2 (a0==a1, b0==b1, a0!=b0):
        #     a0=a1=0 -> 00, b0=b1=1 ->11 : (0,0,1,1)=0011
        #     a0=a1=1 -> 11, b0=b1=0 ->00 : (1,1,0,0)=1100
        # Total decoded_equal patterns: 0000,0101,1010,1111,0011,1100  (6 patterns)
        # anc should be decoded_diff = NOT decoded_equal. Compute decoded_equal onto anc via 6 mcx
        # with appropriate open/closed controls, then X(anc).
        equal_patterns = [
            (0, 0, 0, 0),
            (0, 1, 0, 1),
            (1, 0, 1, 0),
            (1, 1, 1, 1),
            (0, 0, 1, 1),
            (1, 1, 0, 0),
        ]
        ctrls = [a0, a1, b0, b1]
        for pat in equal_patterns:
            zeros = [ctrls[i] for i in range(4) if pat[i] == 0]
            for z in zeros:
                qc.x(z)
            qc.mcx(ctrls, anc)
            for z in zeros:
                qc.x(z)
        qc.x(anc)  # anc = decoded_diff

    def color_diff_uncompute(u, v, anc):
        a0, a1 = qb(u)
        b0, b1 = qb(v)
        equal_patterns = [
            (0, 0, 0, 0),
            (0, 1, 0, 1),
            (1, 0, 1, 0),
            (1, 1, 1, 1),
            (0, 0, 1, 1),
            (1, 1, 0, 0),
        ]
        ctrls = [a0, a1, b0, b1]
        qc.x(anc)
        for pat in reversed(equal_patterns):
            zeros = [ctrls[i] for i in range(4) if pat[i] == 0]
            for z in zeros:
                qc.x(z)
            qc.mcx(ctrls, anc)
            for z in zeros:
                qc.x(z)

    # Compute each edge's diff flag.
    for (u, v), anc in zip(edges, edge_anc):
        color_diff_compute(u, v, anc)

    # Phase -1 iff all edge flags are 1 (all edges properly colored).
    qc.h(final)
    qc.x(final)
    qc.mcx(edge_anc, final)
    qc.x(final)
    qc.h(final)

    # Uncompute edge flags.
    for (u, v), anc in zip(edges, edge_anc):
        color_diff_uncompute(u, v, anc)
