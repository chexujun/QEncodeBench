from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 2), (0, 5), (1, 2), (1, 3), (2, 3), (3, 4), (3, 5)]

    def vq(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # ancilla layout: a_eq[k] flags edge k monochromatic, aggregated into final
    edge_flag = ancilla_qubits[0]   # per-edge "same color" flag (reused)
    acc = ancilla_qubits[1]         # accumulator: 1 if any edge monochromatic
    t0 = ancilla_qubits[2]          # temp
    t1 = ancilla_qubits[3]          # temp

    # We build acc = OR over edges of same_color(edge).
    # f(x)=1 iff no edge monochromatic, i.e. acc==0 -> phase -1 when acc==0.
    # We compute acc, then apply phase for acc==0 (X-sandwiched Z on acc),
    # then uncompute acc.

    def color_equal_compute(u, v, out):
        # colors equal (after 11->00 decode) means: decode(u)==decode(v).
        # decode: c in {0,1,2,3}, with 3->0. color(u)==color(v) as decoded.
        # Equivalent boolean: treat (b0,b1). color 0 codes: {00,11}; 1:{01}; 2:{10}.
        # equal iff same color class.
        # Build class membership then compare. Use t0,t1 as scratch (must be |0>).
        u0, u1 = vq(u)
        v0, v1 = vq(v)
        # is_color0(u) = (u0==u1)  -> XNOR(u0,u1)
        # is_color1(u) = (u0 & ~u1)
        # is_color2(u) = (~u0 & u1)
        # colors equal iff (c0u&c0v) | (c1u&c1v) | (c2u&c2v).
        # We'll set 'out' via three controlled contributions using t0 as a
        # single-class-match indicator, XOR-accumulated into out. Since the
        # three class-matches are mutually exclusive, XOR == OR here.

        # --- class 0 match: (u0 XNOR u1) AND (v0 XNOR v1) ---
        # compute p = u0 XNOR u1 into t0
        qc.x(u0)
        qc.cx(u0, t0)
        qc.x(u0)
        qc.cx(u1, t0)
        qc.x(t0)  # t0 = u0 XNOR u1
        # compute q = v0 XNOR v1 into t1
        qc.x(v0)
        qc.cx(v0, t1)
        qc.x(v0)
        qc.cx(v1, t1)
        qc.x(t1)  # t1 = v0 XNOR v1
        qc.ccx(t0, t1, out)
        # uncompute t1
        qc.x(t1)
        qc.cx(v1, t1)
        qc.x(v0)
        qc.cx(v0, t1)
        qc.x(v0)
        # uncompute t0
        qc.x(t0)
        qc.cx(u1, t0)
        qc.x(u0)
        qc.cx(u0, t0)
        qc.x(u0)

        # --- class 1 match: (u0 & ~u1) AND (v0 & ~v1) ---
        qc.x(u1)
        qc.ccx(u0, u1, t0)  # t0 = u0 & ~u1
        qc.x(u1)
        qc.x(v1)
        qc.ccx(v0, v1, t1)  # t1 = v0 & ~v1
        qc.x(v1)
        qc.ccx(t0, t1, out)
        qc.x(v1)
        qc.ccx(v0, v1, t1)
        qc.x(v1)
        qc.x(u1)
        qc.ccx(u0, u1, t0)
        qc.x(u1)

        # --- class 2 match: (~u0 & u1) AND (~v0 & v1) ---
        qc.x(u0)
        qc.ccx(u0, u1, t0)  # t0 = ~u0 & u1
        qc.x(u0)
        qc.x(v0)
        qc.ccx(v0, v1, t1)  # t1 = ~v0 & v1
        qc.x(v0)
        qc.ccx(t0, t1, out)
        qc.x(v0)
        qc.ccx(v0, v1, t1)
        qc.x(v0)
        qc.x(u0)
        qc.ccx(u0, u1, t0)
        qc.x(u0)

    def color_equal_uncompute(u, v, out):
        color_equal_compute(u, v, out)  # self-inverse: repeating clears 'out'

    # Compute acc = OR of edge_flag over all edges.
    # Strategy: for each edge, compute edge_flag=same_color, then acc |= edge_flag,
    # then uncompute edge_flag. acc |= flag via: acc = acc OR flag.
    # OR(acc, flag): acc' = acc | flag = NOT(NOT acc AND NOT flag).
    # Implement with: if flag and acc==0 -> set acc. Use controlled logic:
    # acc <- acc XOR (flag AND NOT acc). Equivalent: ccx(flag,?,...). Simpler:
    # since we only need acc==0 test at end, accumulate parity won't work (OR!=XOR).
    # Use: for setting OR, apply X on acc, then whenever flag=1 clear acc's "allzero".
    # Cleaner: maintain acc as "all edges proper so far" AND-chain.
    # Let acc represent NAND accumulation: we want final test acc==0 meaning no mono.
    # Use OR gate primitive:
    def or_into(flag, target):
        # target = target OR flag
        qc.x(flag)
        qc.x(target)
        qc.ccx(flag, target, target) if False else None
        # proper OR: target = 1 - (1-target)(1-flag)
        # after X on both, we have ~target,~flag; AND them into a fresh bit is needed.
        # Do it directly: target' = ~(~target & ~flag).
        # We'll compute using a controlled approach without extra ancilla:
        # target currently holds ~target. Multiply by ~flag via CX won't AND.
        # Revert and use different method.
        qc.x(target)
        qc.x(flag)
        # OR via: if target==0, copy flag. i.e. cx(flag,target) gives XOR, wrong when both 1.
        # But target starts at 0 before first edge; and OR of exclusive-ish flags.
        # Safe general OR needs an ancilla AND. Use t (already free here? t0/t1 free).
        qc.x(target)
        qc.x(flag)
        qc.ccx(target, flag, ancilla_qubits[2])  # note: t0 free at this point
        qc.x(target)
        qc.x(flag)
        qc.cx(ancilla_qubits[2], target)
        # undo the AND ancilla
        qc.x(target)  # target now updated; recompute AND to clear scratch
        # (scratch clearing handled below)

    # The above OR helper is fragile; use a robust De Morgan OR with dedicated scratch.
    # Reset: implement acc as AND of (edge proper). proper_k = NOT same_color_k.
    # acc_all_proper via AND chain, phase when acc_all_proper==1.
    # AND chain with two-ancilla scratch:

    # We restart the accumulation logic cleanly here:
    # Use edge_flag = current edge same_color, acc = running "any mono" via OR.
    # Robust OR(target|=flag) using scratch s (must return |0>):
    def robust_or(flag, target, s):
        qc.x(flag)
        qc.x(target)
        qc.ccx(flag, target, s)   # s = ~flag & ~target = ~(target|flag)
        qc.x(flag)
        qc.x(target)
        qc.x(s)                   # s = target|flag
        qc.cx(s, target) if False else None
        # set target = s, but target may already be 1; we want target=s.
        # target = s XOR (s AND target_old)?? To assign, clear then copy.
        # Since s = target|flag >= target, and we want target=s:
        # target_new = s. Do: cx from s only where differ. differ = s & ~target.
        qc.x(target)
        qc.ccx(s, target, target) if False else None
        qc.x(target)
        # Simplest correct assignment: target ^= (s & ~target)
        qc.x(target)
        qc.ccx(s, target, flag) if False else None
        qc.x(target)
        # This is getting circular. Abandon in-place assign; instead keep s AS acc.

    # ---- Clean final implementation ----
    # Compute per-edge same_color into a fresh ancilla each; OR by NOT-AND on a
    # single running bit using the identity that we only test acc==0 at the end.
    # We use: acc holds "all proper so far" (AND). Start acc=1 (X), then for each
    # edge: acc = acc AND proper_edge = acc AND (NOT same_color). Phase when acc==1.

    # Rebuild from scratch, ignoring helpers above.
    for q in [edge_flag, acc, t0, t1]:
        pass

    # acc := 1
    qc.x(acc)
    for (u, v) in edges:
        # edge_flag = same_color(u,v)
        color_equal_compute(u, v, edge_flag)
        # proper = NOT edge_flag ; acc = acc AND proper
        # new_acc = acc AND (NOT edge_flag). Since acc only decreases, and we need
        # to test acc==1 at end (all proper), do controlled clear:
        # if edge_flag==1 then acc:=0. i.e. acc = acc AND ~edge_flag.
        # acc ^= (acc & edge_flag): when edge_flag=1, flips acc from its value to 0
        # only if acc currently 1 -> ccx(acc,edge_flag,acc) invalid (control==target).
        # Use: cx-style via edge_flag controlling: if edge_flag=1 and acc=1 -> acc=0.
        # ccx(edge_flag, acc, t0)? then... simplest: mcx clearing using extra:
        qc.ccx(edge_flag, acc, t0)   # t0 = edge_flag & acc
        qc.cx(t0, acc)               # acc ^= t0  => acc becomes acc AND ~edge_flag
        qc.ccx(edge_flag, acc, t0)   # uncompute t0 (acc already updated: if edge_flag=1,acc now 0 -> t0 stays; recompute clears)
        # uncompute edge_flag
        color_equal_uncompute(u, v, edge_flag)

    # phase: -1 when acc==1 (all edges proper)
    qc.z(acc)

    # uncompute acc back to |0>: reverse the accumulation
    for (u, v) in reversed(edges):
        color_equal_compute(u, v, edge_flag)
        qc.ccx(edge_flag, acc, t0)
        qc.cx(t0, acc)
        qc.ccx(edge_flag, acc, t0)
        color_equal_uncompute(u, v, edge_flag)
    qc.x(acc)
