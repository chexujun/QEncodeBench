from qiskit import QuantumCircuit
from math import pi

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    v0, v1, v2, v3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]
    edges = [(0, 1), (0, 2), (0, 3), (1, 3), (2, 3)]

    edge_anc = ancilla_qubits[0:5]      # one ancilla per edge (covered flag)
    cnt = ancilla_qubits[5:7]           # 2-qubit popcount register (counts up to 4)
    result = ancilla_qubits[7]          # final predicate flag

    p = [v0, v1, v2, v3]

    # --- compute: edge covered flags (OR of two endpoints) ---
    # cover(a,b) = a OR b = NOT( (NOT a) AND (NOT b) ); compute directly:
    # set edge_anc = a OR b via: edge = a xor b xor (a and b)
    for (u, v), ea in zip(edges, edge_anc):
        qc.cx(p[u], ea)
        qc.cx(p[v], ea)
        qc.ccx(p[u], p[v], ea)   # now ea = u OR v

    # --- compute: popcount of x into cnt (2 bits, ripple) ---
    # add each problem bit into the 2-bit counter cnt[0]=LSB, cnt[1]=MSB
    for b in p:
        # carry = cnt0 AND b -> add to cnt1
        qc.ccx(b, cnt[0], cnt[1])
        # cnt0 ^= b
        qc.cx(b, cnt[0])
    # cnt holds popcount mod 4; since max popcount here can be 4 (=100 binary),
    # popcount==4 would wrap to 0 in 2 bits. Handle: size<=2 means cnt in {0,1,2}
    # popcount 3 -> cnt=11, popcount 4 -> cnt=00 (wrap). We need a 3rd bit to be safe.
    # Use an extra guard: detect overflow. But budget limits ancillas.
    # size<=2 <=> MSB==0 AND NOT(cnt==... ) -> size<=2 means cnt in {00,01,10}=>NOT(cnt0 AND cnt1)
    # However popcount 4 wraps to 00 (looks like size 0) -> wrongly accepted.
    # But size-4 cover: all vertices in S is a valid cover but size 4 > 2, must reject.
    # Guard needed. We recompute below with proper handling.

    # size_ok = NOT( cnt0 AND cnt1 )  (rejects size==3). Need also reject size==4.
    # Detect popcount==4: all four problem bits are 1.
    # result = (all edges covered) AND size_ok AND NOT(all four ones)
    # all edges covered = AND of edge_anc (5 flags)
    # We build result using edge flags + size condition.

    # Compute size_ok into result-friendly form using cnt:
    # We want mark condition C = coveredAll AND (size<=2).
    # size<=2 true when NOT(cnt0 AND cnt1) AND NOT(v0 AND v1 AND v2 AND v3)

    # phase: apply -1 when C holds. Use multi-controlled Z with all positive controls
    # on edge_anc (5), and we need size<=2 as controls too. Express via De Morgan:
    # Instead flip: we apply phase when covered AND size<=2.
    # size<=2 is not a simple product, so decompose marking into the allowed set.
    # Enumerate size condition through cnt bits:
    #   size in {0,1,2} corresponds to (cnt1,cnt0) in {00,01,10} EXCEPT the size-4 wrap 00.
    # So among covered states, distinguish size-4 (all ones) explicitly.

    # controls list for "covered": all 5 edge flags = 1
    # We build phase = -1 for covered AND size<=2.
    # Apply mcp(pi) controlled on [edge_anc(5)] and on the size predicate encoded as:
    #   NOT(cnt0 & cnt1)  -> we cannot directly control on a NOT-AND, so compute into result.

    # Compute result = size<=2 indicator (1 if size in {0,1,2} genuinely):
    # start result=1, then zero it out for size3 and size4.
    qc.x(result)                                   # result = 1
    qc.ccx(cnt[0], cnt[1], result)                 # size==3 -> flip to 0
    qc.mcx([v0, v1, v2, v3], result)               # size==4 -> flip to 0 (from wrap it's fine)

    # Now phase -1 when all edges covered AND result==1
    qc.mcp(pi, edge_anc + [result], edge_anc[0] if False else result) if False else None
    qc.mcp(pi, edge_anc[:-1] + [result], edge_anc[-1])

    # --- uncompute result ---
    qc.mcx([v0, v1, v2, v3], result)
    qc.ccx(cnt[0], cnt[1], result)
    qc.x(result)

    # --- uncompute popcount ---
    for b in reversed(p):
        qc.cx(b, cnt[0])
        qc.ccx(b, cnt[0], cnt[1])

    # --- uncompute edge flags ---
    for (u, v), ea in zip(reversed(edges), reversed(edge_anc)):
        qc.ccx(p[u], p[v], ea)
        qc.cx(p[v], ea)
        qc.cx(p[u], ea)
