from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "0100"
    L = len(pattern)
    n_offsets = 2  # offsets 0..1

    # ancilla_qubits[0], [1] are per-offset match flags; ancilla_qubits[2] is the OR flag.
    offset_flags = [ancilla_qubits[0], ancilla_qubits[1]]
    or_flag = ancilla_qubits[2]

    def compute_offset(o, flag):
        # Determine the problem qubits that must equal specified pattern bits.
        controls = []
        zeros = []  # qubits needing X to turn 0-required into control-on-1
        for i, pc in enumerate(pattern):
            if pc == '?':
                continue
            q = problem_qubits[o + i]
            controls.append(q)
            if pc == '0':
                zeros.append(q)
        # X the zero-required qubits so that all controls being 1 means match.
        for q in zeros:
            qc.x(q)
        if controls:
            qc.mcx(controls, flag)
        else:
            qc.x(flag)
        # uncompute the X on zero-required qubits (they are just controls, restore text)
        for q in zeros:
            qc.x(q)

    # Compute each offset flag.
    for o in range(n_offsets):
        compute_offset(o, offset_flags[o])

    # OR of the two offset flags into or_flag:
    # or_flag = f0 OR f1 = NOT( (NOT f0) AND (NOT f1) )
    qc.x(offset_flags[0])
    qc.x(offset_flags[1])
    qc.x(or_flag)
    qc.ccx(offset_flags[0], offset_flags[1], or_flag)
    qc.x(offset_flags[1])
    qc.x(offset_flags[0])

    # Apply the phase on the OR flag.
    qc.z(or_flag)

    # Uncompute the OR flag (mirror).
    qc.x(offset_flags[0])
    qc.x(offset_flags[1])
    qc.ccx(offset_flags[0], offset_flags[1], or_flag)
    qc.x(or_flag)
    qc.x(offset_flags[1])
    qc.x(offset_flags[0])

    # Uncompute each offset flag (mirror of compute).
    for o in reversed(range(n_offsets)):
        compute_offset(o, offset_flags[o])
