from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Oracle for 3-coloring constraint: apply phase -1 iff all edges connect
    vertices of different colors (after decoding 2-bit codes surjectively to 3 colors).
    """
    edges = [(0, 1), (0, 3), (1, 3), (2, 3), (2, 4)]
    a = ancilla_qubits
    
    # Compute edge validity: a[0:5] store whether each edge is "good" (colors differ)
    # a[5] accumulates the AND of all validities
    for i, (u, v) in enumerate(edges):
        compute_colors_differ(qc, problem_qubits, u, v, a[i])
    
    # Build AND tree: start with a[5] = 1, then AND-in each validity
    qc.x(a[5])
    for i in range(5):
        # Update: a[5] := a[5] AND a[i]
        # Method: if NOT a[i], zero out a[5]
        qc.x(a[i])
        qc.ccx(a[5], a[i], a[5])
        qc.x(a[i])
    
    # Apply phase -1 controlled by a[5] (1 iff all edges valid)
    qc.z(a[5])
    
    # Uncompute AND tree
    for i in reversed(range(5)):
        qc.x(a[i])
        qc.ccx(a[5], a[i], a[5])
        qc.x(a[i])
    qc.x(a[5])
    
    # Uncompute edge validities
    for i in reversed(range(5)):
        u, v = edges[i]
        uncompute_colors_differ(qc, problem_qubits, u, v, a[i])


def compute_colors_differ(qc: QuantumCircuit, problem_qubits: list[int],
                          u: int, v: int, result: int) -> None:
    """
    Compute whether vertices u and v decode to different colors into result qubit.
    Colors are same iff one of: both color 0 (b0==b1), both color 1 (code 01),
    or both color 2 (code 10).
    """
    b0_u = problem_qubits[2*u]
    b1_u = problem_qubits[2*u + 1]
    b0_v = problem_qubits[2*v]
    b1_v = problem_qubits[2*v + 1]
    
    # Helper: compute (q0 == q1) into temp via temp = q0 XNOR q1
    def compute_xnor(q0, q1, temp):
        qc.cx(q0, temp)
        qc.cx(q1, temp)
        qc.x(temp)
    
    def uncompute_xnor(q0, q1, temp):
        qc.x(temp)
        qc.cx(q1, temp)
        qc.cx(q0, temp)
    
    # We'll compute same_color = cond1 OR cond2 OR cond3 into result
    # cond1 = (b0_u XNOR b1_u) AND (b0_v XNOR b1_v)
    # cond2 = (b0_u AND NOT b1_u) AND (b0_v AND NOT b1_v)
    # cond3 = (NOT b0_u AND b1_u) AND (NOT b0_v AND b1_v)
    
    # Compute XNOR for u into shared temp, then use ancilla logic
    temp = 15  # Placeholder for internal computation
    
    # cond1: both have b0==b1 (both color 0)
    compute_xnor(b0_u, b1_u, temp)
    qc.ccx(temp, b1_v, result)  # result = (b0_u==b1_u) AND b1_v
    qc.x(b0_v)
    qc.x(b1_v)
    qc.ccx(b0_v, b1_v, result)  # result OR= (b0_v==b1_v) via NOT logic
    qc.x(b0_v)
    qc.x(b1_v)
    uncompute_xnor(b0_u, b1_u, temp)
    
    # cond2: both have code 01
    qc.x(b1_u)
    qc.x(b1_v)
    qc.ccx(b0_u, b1_u, temp)
    qc.ccx(temp, b0_v, temp)
    qc.ccx(temp, b1_v, result)
    qc.x(b1_u)
    qc.x(b1_v)
    
    # cond3: both have code 10
    qc.x(b0_u)
    qc.x(b0_v)
    qc.ccx(b0_u, b1_u, temp)
    qc.ccx(temp, b0_v, temp)
    qc.ccx(temp, b1_v, result)
    qc.x(b0_u)
    qc.x(b0_v)
    
    # Flip result to get "different colors"
    qc.x(result)


def uncompute_colors_differ(qc: QuantumCircuit, problem_qubits: list[int],
                            u: int, v: int, result: int) -> None:
    """Undo compute_colors_differ by running the circuit in reverse."""
    b0_u = problem_qubits[2*u]
    b1_u = problem_qubits[2*u + 1]
    b0_v = problem_qubits[2*v]
    b1_v = problem_qubits[2*v + 1]
    temp = 15
    
    qc.x(result)
    qc.x(b0_u)
    qc.x(b0_v)
    qc.ccx(temp, b1_v, result)
    qc.ccx(temp, b0_v, temp)
    qc.ccx(b0_u, b1_u, temp)
    qc.x(b0_u)
    qc.x(b0_v)
    
    qc.x(b1_u)
    qc.x(b1_v)
    qc.ccx(temp, b1_v, result)
    qc.ccx(temp, b0_v, temp)
    qc.ccx(b0_u, b1_u, temp)
    qc.x(b1_u)
    qc.x(b1_v)
    
    qc.x(b0_v)
    qc.x(b1_v)
    qc.ccx(b0_v, b1_v, result)
    qc.x(b0_v)
    qc.x(b1_v)
    qc.ccx(temp, b1_v, result)
    qc.x(b0_u)
    qc.x(b1_u)
    qc.cx(b1_u, temp)
    qc.cx(b0_u, temp)
    qc.x(temp)
