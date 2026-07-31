import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 2), (0, 3), (0, 4), (1, 4), (2, 3), (3, 4)]

    def qb(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # Two ping-pong accumulators for a running AND of "edge is proper",
    # plus one scratch for the per-edge monochromatic flag.
    accA = ancilla_qubits[0]
    accB = ancilla_qubits[1]
    mono = ancilla_qubits[2]
    # ancilla_qubits[3] unused

    # mono(u,v) -> t (t assumed |0>), no extra scratch: three mutually
    # exclusive 4-control MCX (both color0 via its two bit-patterns 00/00 and
    # 11/11, both color1 = 01/01, both color2 = 10/10).
    def compute_mono(u, v, t):
        u_lo, u_hi = qb(u)
        v_lo, v_hi = qb(v)
        # both color 0, pattern 00/00
        qc.x(u_lo); qc.x(u_hi); qc.x(v_lo); qc.x(v_hi)
        qc.mcx([u_lo, u_hi, v_lo, v_hi], t)
        qc.x(u_lo); qc.x(u_hi); qc.x(v_lo); qc.x(v_hi)
        # both color 0, pattern 11/11
        qc.mcx([u_lo, u_hi, v_lo, v_hi], t)
        # both color 1, pattern 01/01  (lo=1, hi=0)
        qc.x(u_hi); qc.x(v_hi)
        qc.mcx([u_lo, u_hi, v_lo, v_hi], t)
        qc.x(u_hi); qc.x(v_hi)
        # both color 2, pattern 10/10  (lo=0, hi=1)
        qc.x(u_lo); qc.x(v_lo)
        qc.mcx([u_lo, u_hi, v_lo, v_hi], t)
        qc.x(u_lo); qc.x(v_lo)

    # Build running AND of proper_e = (NOT mono_e) into a ping-pong chain, then
    # phase on the final flag, then exactly reverse everything.

    ops = []  # record accumulator targets used, to mirror for uncompute

    # good_{-1} = 1 on accA
    qc.x(accA)

    cur = accA
    nxt = accB
    edge_targets = []
    for (u, v) in edges:
        compute_mono(u, v, mono)     # mono = 1 iff edge monochromatic
        qc.x(mono)                   # mono = proper flag (1 iff colors differ)
        qc.ccx(cur, mono, nxt)       # nxt = good_prev AND proper   (nxt was |0>)
        edge_targets.append((u, v, cur, nxt, mono))
        cur, nxt = nxt, cur          # ping-pong; old `cur` will be cleaned later

    # `cur` now holds good_final = 1 iff all edges proper -> the marked set.
    qc.z(cur)                        # phase -1 on good_final == 1

    # Uncompute: reverse the chain exactly.
    for (u, v, prev_acc, new_acc, m) in reversed(edge_targets):
        qc.ccx(prev_acc, m, new_acc) # undo the Toffoli (new_acc back to |0>)
        qc.x(m)                      # undo proper flip
        compute_mono(u, v, m)        # undo mono (self-inverse) -> m back to |0>

    qc.x(accA)                       # undo good_{-1}
