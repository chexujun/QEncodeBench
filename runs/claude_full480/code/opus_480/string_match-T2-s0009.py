from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # pattern = "11?10" -> compare positions 0,1,3,4 (2 is wildcard)
    # match at offset o: s_o=1, s_{o+1}=1, s_{o+3}=1, s_{o+4}=0
    offsets = [0, 1, 2]
    flags = [ancilla_qubits[i] for i in range(len(offsets))]

    def compute_flag(o, flag):
        c0 = problem_qubits[o]
        c1 = problem_qubits[o + 1]
        c3 = problem_qubits[o + 3]
        c4 = problem_qubits[o + 4]
        qc.x(c4)                      # negate: need s_{o+4} == 0
        qc.mcx([c0, c1, c3, c4], flag)
        qc.x(c4)

    # compute all offset match flags
    for o, flag in zip(offsets, flags):
        compute_flag(o, flag)

    # phase -1 iff any flag == 1 (global -1 accepted):
    # add pi phase to the all-flags-zero state, i.e. all-ones after negation
    for flag in flags:
        qc.x(flag)
    qc.mcp(np.pi, flags[:-1], flags[-1])
    for flag in flags:
        qc.x(flag)

    # uncompute flags back to |0>
    for o, flag in zip(offsets, flags):
        compute_flag(o, flag)
