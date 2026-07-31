import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    edges = [(0, 1), (1, 4), (2, 4), (3, 4)]

    edge_anc = ancilla_qubits[0:4]      # one ancilla per edge (OR of endpoints)
    count_anc = ancilla_qubits[4:7]     # 3 bits: popcount of x (0..5 needs 3 bits)
    # We reuse: total ancillas = 4 + 3 = 7. Need the final predicate flag too.
    # Repurpose one edge ancilla region? We have exactly 7. Use count on 3 bits,
    # 4 edge bits, and fold the phase using an MCP on collected conditions.

    # --- compute edge OR ancillas: a = u OR v = NOT( NOT u AND NOT v ) ---
    for k, (u, v) in enumerate(edges):
        a = edge_anc[k]
        qc.x(x[u]); qc.x(x[v])
        qc.ccx(x[u], x[v], a)   # a = (NOT? ) -> currently a = u AND v after x? compute carefully
        qc.x(x[u]); qc.x(x[v])
        qc.x(a)
        # Now a = NOT(NOT u AND NOT v) = u OR v.
        # Explanation: with x on u,v then ccx: a ^= (NOT u_orig)&(NOT v_orig).
        # then x(a): a = 1 XOR that = NOT(NOT u AND NOT v) = u OR v (since a started 0).

    # --- compute popcount of the 5 problem bits into 3-bit register count_anc ---
    c0, c1, c2 = count_anc[0], count_anc[1], count_anc[2]
    for xi in x:
        # add 1 (controlled by xi) into 3-bit counter [c0,c1,c2], c0 = LSB.
        # carry chain: c2 ^= xi & c1 & c0 ; c1 ^= xi & c0 ; c0 ^= xi
        qc.ccx(xi, c1, c2)  # placeholder ordering; fix below with proper controls
        # (proper full-adder increment)
    # The above loop is not a correct incrementer; replace with explicit increment.

    # NOTE: to keep this correct and self-contained, undo the wrong loop is messy.
    # Instead we abandon the naive loop approach above by NOT relying on it:
    # (The wrong ccx block cancels out because we now redo increment correctly.)
    # -- Redo: first uncompute the bogus block --
    for xi in reversed(x):
        qc.ccx(xi, c1, c2)

    # Correct controlled increment of [c0(LSB), c1, c2] by xi:
    for xi in x:
        qc.ccx(xi, c1, c2)  # if c0 and c1 already 1, and adding via xi&c0... need c0 too
    # This is still not a clean incrementer; undo it too.
    for xi in reversed(x):
        qc.ccx(xi, c1, c2)

    # Clean incrementer per control bit xi (add 1 into 3-bit counter):
    def inc(xi):
        # c2 ^= xi & c1 & c0
        qc.mcx([xi, c0, c1], c2)
        # c1 ^= xi & c0
        qc.ccx(xi, c0, c1)
        # c0 ^= xi
        qc.cx(xi, c0)

    def uninc(xi):
        qc.cx(xi, c0)
        qc.ccx(xi, c0, c1)
        qc.mcx([xi, c0, c1], c2)

    for xi in x:
        inc(xi)

    # Predicate: all 4 edge ancillas == 1  AND  count <= 3.
    # count <= 3 means NOT(count >= 4) i.e. c2==0 OR (c2==1 and count==4 or 5 -> c2 set).
    # popcount max 5 -> c2 (value 4) set iff count in {4,5}. count<=3 iff c2==0.
    # So predicate = (all edges) AND (c2 == 0).
    controls = list(edge_anc) + [c2]
    # We want phase -1 when all edge_anc==1 and c2==0.
    qc.x(c2)  # so condition becomes all controls == 1
    # Apply multi-controlled Z (phase) on these controls:
    from qiskit.circuit.library import ZGate
    qc.h(controls[-1])
    qc.mcx(controls[:-1], controls[-1])
    qc.h(controls[-1])
    qc.x(c2)

    # --- uncompute counter ---
    for xi in reversed(x):
        uninc(xi)

    # --- uncompute edge ancillas (mirror) ---
    for k, (u, v) in enumerate(edges):
        a = edge_anc[k]
        qc.x(a)
        qc.x(x[u]); qc.x(x[v])
        qc.ccx(x[u], x[v], a)
        qc.x(x[u]); qc.x(x[v])
