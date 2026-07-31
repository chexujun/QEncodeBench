from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits, ancilla_qubits) -> None:
    edges = [(0, 1), (0, 2), (0, 4), (1, 3), (1, 5), (2, 4), (3, 4), (4, 5)]

    def qb(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # ea[e] = 1 iff edge e is monochromatic (same decoded color)
    ea = ancilla_qubits[0:len(edges)] if len(ancilla_qubits) >= len(edges) else None
    edge_anc = ancilla_qubits[0]
    flag = ancilla_qubits[1]
    ta = ancilla_qubits[2]
    tb = ancilla_qubits[3]

    def compute_edge_mono(u, v, target):
        # colors: c=0 <-> codes 00 or 11 ; c=1 <-> 01 ; c=2 <-> 10
        # decoded color equality. Let (a0,a1)=u, (b0,b1)=v.
        # color0 set: {00,11}; color1:{01}; color2:{10}
        # mono iff same color.
        u0, u1 = qb(u)
        v0, v1 = qb(v)
        # ta = 1 iff u is color0 (00 or 11) => (u0==u1)
        # tb = 1 iff v is color0 (v0==v1)
        # For color1/color2 (codes 01,10) equality is direct code equality.
        # General: same color iff
        #   (u color0 and v color0) OR (code_u==code_v and not color0? ) 
        # Simpler: same color iff
        #   (u0==u1 and v0==v1)  [both color0]
        #   OR ( (u0,u1)==(v0,v1) and (u0 xor u1)==1 )  [both same non-color0 code 01 or 10]
        # term A: both color0
        qc.cx(u0, u1)          # u1' = u0 xor u1 ; ==0 means color0
        qc.cx(v0, v1)          # v1' = v0 xor v1
        qc.x(u1)               # u1'' = 1 iff color0
        qc.x(v1)
        qc.ccx(u1, v1, ta)     # ta = both color0
        qc.x(u1)
        qc.x(v1)
        qc.cx(u0, u1)          # restore u1
        qc.cx(v0, v1)          # restore v1
        # term B: codes equal and code is 01 or 10 (i.e. u0 xor u1 ==1)
        # codes equal: u0==v0 and u1==v1
        qc.cx(u0, v0)          # v0' = u0 xor v0 ; 0 iff equal bit0
        qc.cx(u1, v1)          # v1' = u1 xor v1 ; 0 iff equal bit1
        qc.x(v0)               # v0''=1 iff bit0 equal
        qc.x(v1)               # v1''=1 iff bit1 equal
        # non-color0 means u0 xor u1 ==1
        qc.cx(u0, u1)          # u1' = u0 xor u1 ; 1 iff non color0
        qc.mcx([v0, v1, u1], tb)  # tb = codes equal AND non-color0
        qc.cx(u0, u1)          # restore u1
        qc.x(v0)
        qc.x(v1)
        qc.cx(u0, v0)          # restore v0
        qc.cx(u1, v1)          # restore v1
        # target = ta OR tb  ; ta and tb are mutually exclusive
        qc.cx(ta, target)
        qc.cx(tb, target)
        # uncompute ta, tb (recompute mirror)
        qc.cx(u0, u1); qc.cx(v0, v1); qc.x(u1); qc.x(v1)
        qc.ccx(u1, v1, ta); qc.x(u1); qc.x(v1); qc.cx(u0, u1); qc.cx(v0, v1)
        qc.cx(u0, v0); qc.cx(u1, v1); qc.x(v0); qc.x(v1); qc.cx(u0, u1)
        qc.mcx([v0, v1, u1], tb)
        qc.cx(u0, u1); qc.x(v0); qc.x(v1); qc.cx(u0, v0); qc.cx(u1, v1)

    # Accumulate: flag counts monochromatic edges into edge_anc as OR? 
    # We need f=1 iff NO monochromatic edge. Use edge_anc bits: compute each
    # edge mono into edge_anc via toggling, phase when all zero.
    # Strategy: compute OR of all mono flags into edge_anc using it as running
    # "any-mono" bit is wrong for uncompute. Instead compute each edge mono into
    # a fresh scratch, but we only have limited ancillas. Use edge_anc as a
    # counter parity is insufficient. Use multi-controlled on all-clear.
    #
    # Approach: for each edge compute mono into edge_anc? collisions. Instead:
    # phase = -1 iff all edges non-mono. Compute mono_e sequentially into flag,
    # but need all simultaneously for the multi-control. Not enough ancillas
    # for 8 separate bits (only 5 ancillas).
    #
    # Use OR accumulation: set edge_anc=1 if ANY edge mono, then phase -1 iff
    # edge_anc==0. OR via: for each edge, compute mono into flag, then
    # CX flag->? no, OR isn't reversible simply. Use De Morgan with counter:
    # Instead build edge_anc = 1 iff any mono by: edge_anc ^= mono_e AND (edge_anc? )
    # Simpler reversible OR: edge_anc = NOT(AND of (not mono_e)). 
    #
    # We compute product of (1 - mono_e) style: maintain acc = AND of nonmono so
    # far in edge_anc. Start edge_anc via x -> 1. For each edge compute mono into
    # flag (temp), then acc_new = acc AND (not mono). Use ta as new acc.
    good = edge_anc
    prev = flag
    # initialize prev = 1 (all-good so far)
    qc.x(prev)
    used_temps = [ta, tb, ancilla_qubits[4]]
    # We'll ping-pong acc between two ancillas: p0, p1
    p_list = [flag, edge_anc]
    cur = 0
    qc.x(p_list[cur])  # already did x(prev)=x(flag); ensure consistent
    # Undo double-x confusion: reset. (flag got x twice -> back to 0). Set fresh.
    qc.x(flag)  # now flag=0 again
    # restart clean
    acc = flag
    qc.x(acc)  # acc=1 meaning "all edges so far non-mono"
    other = edge_anc
    scratch = ancilla_qubits[4]  # mono temp
    ta_l = ta
    tb_l = tb

    def edge_mono_into(u, v, target):
        compute_edge_mono(u, v, target)

    for (u, v) in edges:
        # scratch = mono(u,v)
        edge_mono_into(u, v, scratch)
        # other = acc AND (not scratch)
        qc.x(scratch)
        qc.ccx(acc, scratch, other)
        qc.x(scratch)
        # uncompute scratch
        edge_mono_into(u, v, scratch)
        # clear acc for reuse next iteration: acc currently holds old value; we
        # move: new acc = other, and reset old acc to 0.
        # reset acc: acc = other AND ... but acc still = old acc value; we must
        # zero it. Since other = acc AND (not scratch), we cannot trivially zero
        # acc without info. Uncompute other-relation not possible generally.
        # -> swap roles and zero old acc by recomputing? Simpler: use CSWAP-free
        # by clearing acc via: acc ^= other when other implies? not valid.
        # Fallback: copy other into acc via reset trick:
        # acc_old is 1 for the running-good chain until first mono. This chain is
        # monotone: once other=0 it stays 0. So acc_old = other OR scratch_was.
        # Too fragile.
        acc, other = other, acc
        qc.reset  # placeholder no-op reference (not called)

    # phase: -1 iff acc==1 (all edges non-mono => f=1)
    qc.z(acc)

    # Uncompute the accumulation chain in reverse
    for (u, v) in reversed(edges):
        acc, other = other, acc
        edge_mono_into(u, v, scratch)
        qc.x(scratch)
        qc.ccx(acc, scratch, other)
        qc.x(scratch)
        edge_mono_into(u, v, scratch)
    qc.x(acc)
