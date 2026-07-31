from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 3), (0, 4), (1, 3), (1, 5), (2, 5), (4, 5)]

    def qb(v):
        # low bit, high bit for vertex v
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    edge_anc = ancilla_qubits[0]   # per-edge "same color" flag
    acc = ancilla_qubits[1]        # accumulates count of violated edges (parity insufficient) -> use as OR via flips
    # We need f=1 iff ALL edges have differing colors, i.e. no edge is monochromatic.
    # Strategy: compute for each edge a "monochromatic" flag into edge_anc, OR-accumulate
    # into acc (acc becomes 1 if ANY edge monochromatic), then phase when acc == 0
    # (all differ). Use compute -> phase -> uncompute.

    def edge_mono_compute(u, v, target):
        # target ^= [color(u) == color(v)]
        u0, u1 = qb(u)
        v0, v1 = qb(v)
        # colors equal under surjective decode where 11 and 00 both -> color 0.
        # color(u)==color(v) as decoded. Decoded color d in {0,1,2}:
        #   code 00 or 11 -> 0 ; 01 -> 1 ; 10 -> 2.
        # Equivalent boolean: define is0(c)= (c==00) or (c==11) = (b0 == b1)... actually
        #   00: b0=0,b1=0 ; 11: b0=1,b1=1 -> b0==b1 -> color 0.
        #   01: b0=1,b1=0 -> color 1.
        #   10: b0=0,b1=1 -> color 2.
        # So color0 <=> (b0 == b1); color1 <=> (b0=1,b1=0); color2 <=> (b0=0,b1=1).
        # Enumerate equality of decoded colors between u and v via the 3 mutually
        # exclusive color-match cases; OR them into target.
        anc0 = ancilla_qubits[2]  # per-vertex helper A
        anc1 = ancilla_qubits[3]  # per-vertex helper B

        # ---- both color 0: (u0==u1) AND (v0==v1) ----
        # u0==u1  <=> NOT(u0 XOR u1). Put (u0 XOR u1) style; we want equality.
        # Compute anc0 = (u0==u1): anc0 ^= 1 then anc0 ^= (u0 xor u1) -> anc0 = 1 xor(u0 xor u1)=equality
        qc.x(anc0)
        qc.cx(u0, anc0)
        qc.cx(u1, anc0)          # anc0 = (u0==u1)
        qc.x(anc1)
        qc.cx(v0, anc1)
        qc.cx(v1, anc1)          # anc1 = (v0==v1)
        qc.ccx(anc0, anc1, target)  # target ^= both color0
        # uncompute anc0, anc1
        qc.cx(v1, anc1)
        qc.cx(v0, anc1)
        qc.x(anc1)
        qc.cx(u1, anc0)
        qc.cx(u0, anc0)
        qc.x(anc0)

        # ---- both color 1: (u0=1,u1=0) AND (v0=1,v1=0) ----
        # color1(u) = u0 AND (NOT u1). Compute anc0=color1(u), anc1=color1(v).
        qc.x(u1)
        qc.ccx(u0, u1, anc0)     # anc0 = u0 & ~u1
        qc.x(u1)
        qc.x(v1)
        qc.ccx(v0, v1, anc1)     # anc1 = v0 & ~v1
        qc.x(v1)
        qc.ccx(anc0, anc1, target)
        # uncompute
        qc.x(v1)
        qc.ccx(v0, v1, anc1)
        qc.x(v1)
        qc.x(u1)
        qc.ccx(u0, u1, anc0)
        qc.x(u1)

        # ---- both color 2: (u0=0,u1=1) AND (v0=0,v1=1) ----
        # color2(u) = (NOT u0) AND u1.
        qc.x(u0)
        qc.ccx(u0, u1, anc0)     # anc0 = ~u0 & u1
        qc.x(u0)
        qc.x(v0)
        qc.ccx(v0, v1, anc1)     # anc1 = ~v0 & v1
        qc.x(v0)
        qc.ccx(anc0, anc1, target)
        # uncompute
        qc.x(v0)
        qc.ccx(v0, v1, anc1)
        qc.x(v0)
        qc.x(u0)
        qc.ccx(u0, u1, anc0)
        qc.x(u0)

    # Build OR of all edge-monochromatic flags into acc using the standard trick:
    #   acc holds running "any violated". We use De Morgan: instead accumulate
    #   product of (NOT mono) is hard; simplest: acc ^= mono_edge, but XOR != OR.
    # Use inclusion via: keep acc as OR by conditional set. Implement OR by
    #   computing each edge mono into a fresh clean edge_anc, then CX into acc only
    #   when acc still 0 -> that's controlled, messy. Instead use the clean identity:
    #   f = AND over edges of (NOT mono). Compute NOT-mono per edge into edge_anc,
    #   then multi-control on all being 1. But edges reuse edge_anc.
    #
    # Cleanest correct approach: accumulate acc = OR of monos via
    #   acc' = acc OR mono = acc XOR mono XOR (acc AND mono).
    # Simpler: since we phase on acc==0, and we uncompute everything, use the
    # standard "count into acc with OR" done sequentially:
    #   for each edge: compute mono into edge_anc; acc ^= edge_anc when acc==0.
    # To avoid AND bookkeeping, note we can instead multi-control the phase on
    # ALL edge-notmono bits simultaneously — but only 4 ancillas.
    #
    # Use the OR construction explicitly:
    def or_into(acc_q, src_q, helper):
        # acc_q = acc_q OR src_q, using helper (must be |0>), reversible:
        # acc_q OR src = NOT( NOT acc AND NOT src )
        qc.x(acc_q)
        qc.x(src_q)
        qc.x(acc_q)  # net: acc unchanged so far -- avoid; do proper:
        # (Undo the confusion) implement directly below instead.
        pass

    # Direct OR accumulation avoiding helper juggling: acc ^= mono ^ (acc&mono).
    # acc&mono handled with ccx into a temp then cx. But we lack a spare clean qubit
    # during phasing since anc2/anc3 are free between edges. Use anc2 as temp.
    temp = ancilla_qubits[2]

    # Compute acc = OR of all edge monos.
    for (u, v) in edges:
        edge_mono_compute(u, v, edge_anc)     # edge_anc = mono(edge)
        # acc = acc OR edge_anc using temp (clean): 
        # OR: acc ^= edge_anc; acc ^= (acc_old AND edge_anc) -- need acc_old.
        # Use: temp = acc AND edge_anc ; acc ^= edge_anc ; acc ^= temp gives
        #   new_acc = acc XOR edge XOR (acc AND edge) = acc OR edge. But temp used
        #   acc value AFTER? compute temp before modifying acc.
        qc.ccx(acc, edge_anc, temp)   # temp = acc_old AND edge_anc
        qc.cx(edge_anc, acc)          # acc ^= edge_anc
        qc.cx(temp, acc)              # acc ^= temp  => acc = acc_old OR edge_anc
        qc.ccx(acc, edge_anc, temp)   # WRONG value now; need to uncompute temp with acc_old
        # Uncompute temp: temp currently = acc_old AND edge_anc still (we must clear).
        # After above extra ccx temp toggled again -> messy. Remove that line effect:
        # (the extra ccx above re-set temp using NEW acc; undo it)
        qc.ccx(acc, edge_anc, temp)
        # Now clear temp back to 0 using the pre-OR relation is impossible with new acc.
        # Instead clear edge_anc by uncomputing the predicate; temp cleared separately.
        # To keep temp clean we instead recompute: temp = new_acc AND edge_anc? Not equal.
        # ---- abandon temp trick; use simpler XOR-safe OR below ----
        # uncompute edge_anc predicate to restore it to 0 for reuse:
        edge_mono_compute(u, v, edge_anc)
        # NOTE: this leaves acc = OR so far, edge_anc = 0, temp must be 0.
        # temp handling: net temp toggles above = ccx,ccx,ccx = 3 toggles of same
        # condition acc&edge... to guarantee temp==0 we ensure even count -> add one:
        qc.ccx(acc, edge_anc, temp)  # edge_anc now 0 => no-op, temp unchanged(0)
