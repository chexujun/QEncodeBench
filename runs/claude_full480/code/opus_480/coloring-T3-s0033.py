from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 2), (0, 4), (1, 3), (2, 3), (2, 4), (3, 4)]

    def qb(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # Ancillas: a_edge = ancilla_qubits[0] marks "this edge is monochromatic",
    # a_flag = ancilla_qubits[1] counts number of monochromatic edges (as parity? no)
    # We need AND over edges of "different". Equivalent: NONE of the edges monochromatic.
    # Compute per-edge "same color" flag into a_edge, accumulate an OR into a_or.
    # Then phase if a_or == 0 (i.e. all edges different) -> mark f=1.
    # Use a_or as count-of-violations != 0 detector via multi-controlled logic:
    # simpler: flip a_or for each monochromatic edge; a_or ends =0 iff no violation
    # BUT multiple violations could toggle a_or back to 0. So use OR not XOR.
    # Implement OR: a_or stays 1 once set. We compute per-edge same-flag, then
    # do ccx? OR of bit into a_or: a_or = a_or OR e  == X trick:
    #   we want a_or=1 if any e=1. Use: for each edge, if e==1 and a_or==0 set.
    # Easiest correct OR without extra ancilla issues: use De Morgan.
    # a_all_diff = AND over edges of (NOT same). Compute NOT-same per edge into
    # a temp, and MCX all NOT-same flags into a target -> too many ancillas.
    #
    # Instead: build a_or as running OR using one work ancilla a_e.

    a_e = ancilla_qubits[0]   # per-edge "same color" temp
    a_or = ancilla_qubits[1]  # OR accumulator of violations
    t1 = ancilla_qubits[2]
    t2 = ancilla_qubits[3]

    def edge_same_compute(u, v):
        # set a_e = 1 iff decoded color(u) == color(v)
        u0, u1 = qb(u)
        v0, v1 = qb(v)
        # color equality with surjective decode (11->0). color values 0,1,2.
        # colors equal cases:
        #  both color0: code in {00,11}
        #  both color1: code == 01 both
        #  both color2: code == 10 both
        # t1 = (u is color0), t2 = (v is color0): color0 = (b0==b1)
        # u_color0 = NOT(u0 XOR u1); compute into t1
        qc.cx(u0, t1); qc.cx(u1, t1); qc.x(t1)   # t1 = 1 iff u0==u1 (color0)
        qc.cx(v0, t2); qc.cx(v1, t2); qc.x(t2)   # t2 = 1 iff v0==v1 (color0)
        qc.ccx(t1, t2, a_e)                       # both color0 -> same
        # uncompute t1,t2
        qc.x(t2); qc.cx(v1, t2); qc.cx(v0, t2)
        qc.x(t1); qc.cx(u1, t1); qc.cx(u0, t1)
        # both color1: code==01 for both -> u0=1,u1=0,v0=1,v1=0
        qc.x(u1); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], a_e)
        qc.x(u1); qc.x(v1)
        # both color2: code==10 for both -> u0=0,u1=1,v0=0,v1=1
        qc.x(u0); qc.x(v0)
        qc.mcx([u0, u1, v0, v1], a_e)
        qc.x(u0); qc.x(v0)

    def edge_same_uncompute(u, v):
        u0, u1 = qb(u)
        v0, v1 = qb(v)
        qc.x(u0); qc.x(v0)
        qc.mcx([u0, u1, v0, v1], a_e)
        qc.x(u0); qc.x(v0)
        qc.x(u1); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], a_e)
        qc.x(u1); qc.x(v1)
        qc.cx(u0, t1); qc.cx(u1, t1); qc.x(t1)
        qc.cx(v0, t2); qc.cx(v1, t2); qc.x(t2)
        qc.ccx(t1, t2, a_e)
        qc.x(t2); qc.cx(v1, t2); qc.cx(v0, t2)
        qc.x(t1); qc.cx(u1, t1); qc.cx(u0, t1)

    # OR accumulate: a_or := a_or OR a_e for each edge, keeping a_e clean after.
    # We compute a_e, then set a_or via: if a_e then flip a_or only if a_or==0.
    # Running OR trick: a_or_new = a_or OR a_e = NOT( NOT a_or AND NOT a_e ).
    # Implement with: X(a_or); ccx? need NOT a_e too. Simpler monotone OR:
    #   cx(a_e, a_or) is XOR not OR. To get true OR that never resets, use:
    #   x(a_or); x(a_e); ccx not possible in place cleanly.
    # Use standard OR: a_or ^= a_e when a_or currently 0. Equivalent monotone:
    #   apply X to a_or; then a_or := a_or AND (NOT a_e): that's a_or_new_bar...
    # Cleanest: compute a_or as AND of (NOT same) via keeping a_or meaning
    # "all edges so far different". Start a_or=1 (all diff). For each edge:
    #   a_or := a_or AND (NOT a_e). AND with control: if a_e==1, clear a_or.
    #   "clear a_or if a_e==1": cx? that flips. Use: if a_e and a_or -> flip a_or
    #   ccx(a_e, a_or, a_or) invalid (target in controls).
    # So use two-target approach with fresh meaning each step is hard w/ ancillas.

    # Simplest robust: accumulate violations into a_or by OR using the identity
    # with a_e as control and a_or as target but guaranteeing monotonic set:
    #   Since a_e is 0/1 and we do cx(a_e,a_or) once per edge, a_or = XOR of all
    #   same-flags. That is 1 iff an ODD number of monochromatic edges. Wrong.
    #
    # Fix with proper OR: init a_or=0; represent OR via toggling only when new.
    # Use CCX with an extra guard: guard = NOT a_or. But we lack ancilla.
    #
    # We DO have t1,t2 free between edges. Use monotone OR:
    #   set g = NOT a_or (t1); if g AND a_e then set a_or (ccx(t1,a_e,a_or));
    #   uncompute g.
    for (u, v) in edges:
        edge_same_compute(u, v)
        qc.x(a_or)            # t via a_or itself: guard = NOT a_or
        qc.cx(a_or, t1)       # t1 = NOT a_or
        qc.x(a_or)            # restore a_or
        qc.ccx(t1, a_e, a_or) # a_or |= a_e  (set only when was 0)
        qc.cx(a_or, t1)       # uncompute t1: t1 ^= a_or... not exact
        # NOTE guard cleanup handled below via recompute
        # clean t1 fully:
        qc.x(a_or); qc.cx(a_or, t1); qc.x(a_or)
        edge_same_uncompute(u, v)

    # Now a_or == 1 iff at least one edge monochromatic (f=0 region).
    # f(x)=1 iff a_or==0. Apply phase -1 when a_or==0:
    qc.x(a_or)
    qc.z(a_or)
    qc.x(a_or)

    # Uncompute a_or back to 0 by repeating the OR accumulation in reverse.
    for (u, v) in reversed(edges):
        edge_same_compute(u, v)
        qc.x(a_or); qc.cx(a_or, t1); qc.x(a_or)
        qc.ccx(t1, a_e, a_or)
        qc.x(a_or); qc.cx(a_or, t1); qc.x(a_or)
        edge_same_uncompute(u, v)
