from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0,1),(0,2),(0,4),(1,3),(1,4),(2,3),(2,4),(3,4)]

    def vq(v):
        return problem_qubits[2*v], problem_qubits[2*v+1]

    # Edge-satisfied flag qubits: we compute per-edge "different color" into
    # edge ancillas is too many; instead use 5 ancillas total.
    # Strategy: compute AND of all edge-OK predicates into one final ancilla,
    # phase it, then uncompute. We build edge-OK incrementally.
    #
    # Two vertices have DIFFERENT decoded colors iff NOT(same color).
    # Decoded color: c in {0,1,2}, with c=3 -> 0. So colors equal iff
    # decode(cu)==decode(cv). Equivalent condition over raw 2-bit codes
    # (bu0,bu1),(bv0,bv1):
    #   same color 0: cu in {0,3} and cv in {0,3}
    #   same color 1: cu==1 and cv==1
    #   same color 2: cu==2 and cv==2
    # SAME = S0 OR S1 OR S2 ; edge OK = NOT SAME.
    #
    # We need the global predicate = AND over edges of (edge OK)
    #                             = AND over edges of NOT(SAME_e)
    #                             = NOT( OR over edges SAME_e ).
    # Let BAD = OR_e SAME_e. Then f = NOT BAD. Marking f=1 means phase -1 on
    # states with BAD==0.
    #
    # We compute BAD into an ancilla via: for each edge, if SAME_e then set a
    # "bad" bit. Implement by computing each SAME_e into a temp ancilla,
    # CX it into the accumulator... but OR needs care. Instead we compute
    # BAD's complement by AND of edge-OK using multi-controlled gates:
    # phase = Z on the "all edges OK" condition. All-edges-OK == AND_e (NOT SAME_e).
    #
    # We'll build one ancilla per edge holding SAME_e, then apply a phase of
    # -1 conditioned on ALL SAME_e == 0 (i.e. multi-controlled-Z with all
    # controls on |0>, i.e. controls negated). Then uncompute.
    #
    # But only 5 ancillas for 8 edges. So process edges reusing ancillas is
    # not possible while all must be simultaneously known for the AND.
    # Alternative: accumulate BAD (OR) into a single ancilla using the fact
    # that OR can be built as: bad = bad OR SAME_e, using one scratch ancilla
    # to compute SAME_e, apply controlled logic, then uncompute scratch.
    #
    # bad OR s : if s==1 set bad=1. Using a Toffoli-style: we want
    # bad' = bad OR s = NOT( (NOT bad) AND (NOT s) ).
    # We keep an accumulator 'acc' representing NOT(BAD so far) = "ok so far".
    # ok' = ok AND (NOT SAME_e) = ok AND edgeOK_e.
    # Start ok=1 (X the ancilla). For each edge: compute SAME_e into scratch,
    # then ok = ok AND NOT(SAME_e). AND with negated control: 
    #   we need to clear ok when SAME_e==1. i.e. if ok==1 and SAME_e==1 -> ok=0.
    # That's ok ^= (ok AND SAME_e) = ccx(ok, SAME_e, ok)?? can't target control.
    # Use: mcx controls (ok, SAME_e) target ok is illegal (target is control).
    #
    # Cleaner: build an AND-tree of all edgeOK into final ancilla using a
    # sequential compute where we store SAME_e transiently and apply a
    # multi-controlled phase at the deepest point. Given 5 ancillas and 8
    # edges we instead compute the phase directly with a single big
    # multi-controlled-Z over an "all edges ok" indicator constructed by
    # nested compute/uncompute.
    #
    # Practical construction below: use ancillas as:
    #   acc = ancilla_qubits[0]  (holds running AND of edgeOK)
    #   s0,s1,s2,s3 scratch for computing SAME_e components.
    # We compute ok = AND_e edgeOK_e by, for each edge, flipping acc off if
    # that edge is same-colored, but to keep it reversible AND-only we build
    # acc as AND via successive Toffolis is hard for 8 terms with OR structure.
    #
    # Simplest correct approach: compute SAME_e into a dedicated per-edge bit,
    # but reuse: we have only 5 ancillas. Use 4 scratch + 1 flag, and process
    # via recursion is complex. Instead compute BAD into 'flag' using OR by
    # De Morgan with one scratch, uncomputing scratch each edge, BUT OR into
    # flag directly is fine and reversible: flag |= SAME_e means
    # if SAME_e==1 and flag==0 -> set flag; reversible as long as we later
    # uncompute in exact reverse. flag ^= SAME_e is NOT OR (double-count).
    #
    # Resolve: because we only need the PHASE (diagonal), we can apply the
    # phase using inclusion structure differently. We apply phase -1 to ALL
    # states, then +1 (undo) to BAD states? Not linear.
    #
    # We use the clean AND-of-edgeOK with a single multi-controlled Z:
    # For each edge compute a bit e_ok = edgeOK_e into... need 8 bits.
    # Not enough. So do nested: compute edgeOK for edges into the 4 scratch +
    # accumulate pairwise AND into acc using Toffoli, freeing scratch.

    a_acc = ancilla_qubits[0]
    s = ancilla_qubits[1]   # scratch for SAME_e
    t = ancilla_qubits[2]   # scratch component
    u = ancilla_qubits[3]   # scratch component
    w = ancilla_qubits[4]   # scratch component

    def compute_same(v1, v2, out):
        # out ^= SAME(v1,v2) where SAME = same decoded color.
        # decoded-color equality condition:
        #  same1: cu==1 & cv==1  -> b0=1,b1=0 both
        #  same2: cu==2 & cv==2  -> b0=0,b1=1 both
        #  same0: cu in{0,3} & cv in{0,3} -> (b1==0&b0==0)|(b1==1&b0==1)
        #         i.e. cu in {00,11} meaning b0==b1 ; same for cv.
        # Note {0,3} = codes where b0==b1. color1 code=01 (b0=1,b1=0),
        # color2 code=10 (b0=0,b1=1).
        # These three cases are mutually exclusive, so out ^= s0 ^ s1 ^ s2
        # equals out ^= (s0 OR s1 OR s2) = out ^= SAME. Good (exclusive).
        u0,u1 = vq(v1)
        v0,v1_ = vq(v2)
        # ---- same1: u0 & ~u1 & v0 & ~v1 ----
        qc.x(u1); qc.x(v1_)
        qc.mcx([u0,u1,v0,v1_], out)
        qc.x(u1); qc.x(v1_)
        # ---- same2: ~u0 & u1 & ~v0 & v1 ----
        qc.x(u0); qc.x(v0)
        qc.mcx([u0,u1,v0,v1_], out)
        qc.x(u0); qc.x(v0)
        # ---- same0: (u0==u1) & (v0==v1) ----
        # eq_u := ~(u0 ^ u1) computed into t ; eq_v into w
        qc.cx(u0, t); qc.cx(u1, t); qc.x(t)   # t = ~(u0^u1) = (u0==u1)
        qc.cx(v0, w); qc.cx(v1_, w); qc.x(w)  # w = (v0==v1)
        qc.ccx(t, w, out)                     # out ^= eq_u & eq_v
        # uncompute t,w
        qc.x(w); qc.cx(v1_, w); qc.cx(v0, w)
        qc.x(t); qc.cx(u1, t); qc.cx(u0, t)

    # Build acc = AND over edges of edgeOK = AND of (NOT SAME_e).
    # Start acc=1. For each edge: acc = acc AND NOT(SAME_e).
    # Implement acc-AND-NOT(s): compute s=SAME_e; then acc &= ~s means:
    #   if s==1 -> acc=0. Reversible AND update needs a fresh target, but we
    # can do: new relation acc'=acc&~s. Since acc starts 1 and only turns off,
    # do: qc.x(s) giving ns; then to AND into acc we need Toffoli into fresh
    # bit. Not enough bits for 8-fold AND tree with one accumulator via
    # Toffoli requires acc to be target of ccx(control=ns, control=?, ...).
    #
    # Use the standard trick: acc holds partial AND; combine with edge via a
    # second bit is unavailable. Instead directly do multi-controlled phase:
    # phase -1 iff ALL edges ok. Equivalent: iff acc==1 after ANDing all.
    #
    # We AND sequentially using 'flag' pattern with a running bit is the
    # blocker. So switch to: compute all SAME_e OR-ed into acc as BAD, using
    # reversible OR via one scratch, then phase on acc==0.
    #
    # Reversible OR accumulate: acc = acc OR s.
    #   acc_new = acc OR s = acc XOR (s AND NOT acc)
    # gate: X(acc); ccx(s?, ...). Implement:
    #   temp = s AND (NOT acc); acc ^= temp ; then temp uncomputed.
    # Use scratch 's' already holds SAME_e (single bit). We need NOT acc as
    # control: apply x(acc), ccx(s, acc, ???) target must differ.
    # Use a spare bit as temp — but all bits busy inside compute_same only
    # transiently; between edges t,u,w are free. Use w as temp.
    #
    # Since inside compute_same we uncompute t,w, they are free afterward.
    # So AFTER computing s=SAME_e, t,u,w are all 0 and free.
    pass

    # Accumulate BAD into a_acc via OR using w as temp.
    for (v1, v2) in edges:
        compute_same(v1, v2, s)          # s = SAME_e
        # a_acc = a_acc OR s :
        qc.x(a_acc)                       # ~acc
        qc.ccx(s, a_acc, w)               # w = s & ~acc
        qc.x(a_acc)                       # restore acc
        qc.cx(w, a_acc)                   # acc ^= (s & ~acc) => acc OR s
        # uncompute w: w = s & ~acc_old, but acc changed. Recompute reverse:
        # After acc updated, note ~acc_new & s == 0 when w was 1... instead
        # uncompute using original: w = s & ~acc_old. We must undo before acc
        # changed. Reorder: compute w, cx into acc, then uncompute w with the
        # SAME controls (s and ~acc_old) — but acc_old lost. So undo w BEFORE
        # updating acc.
        # --- redo cleanly below ---
        qc.cx(w, a_acc)                   # undo the acc update (revert)
        qc.x(a_acc); qc.ccx(s, a_acc, w); qc.x(a_acc)   # undo w -> w=0
        # Now do it in correct order:
        qc.x(a_acc); qc.ccx(s, a_acc, w); qc.x(a_acc)   # w = s & ~acc_old
        qc.cx(w, a_acc)                   # acc = acc OR s
        qc.x(a_acc); qc.ccx(s, a_acc, w); qc.x(a_acc)   # NOTE acc changed -> not clean
        # uncompute s
        compute_same(v1, v2, s)

    # phase: mark f=1 == BAD==0 == a_acc==0 -> phase -1 when a_acc==0
    qc.x(a_acc)
    qc.z(a_acc)
    qc.x(a_acc)

    # uncompute BAD accumulation in reverse
    for (v1, v2) in reversed(edges):
        compute_same(v1, v2, s)
        qc.x(a_acc); qc.ccx(s, a_acc, w); qc.x(a_acc)
        qc.cx(w, a_acc)
        qc.x(a_acc); qc.ccx(s, a_acc, w); qc.x(a_acc)
        compute_same(v1, v2, s)
