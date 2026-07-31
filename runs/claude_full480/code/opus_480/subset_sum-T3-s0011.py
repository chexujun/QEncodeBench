from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [10, 12, 3, 15, 13]
    T = 10
    n = len(a)
    # Sum range: 0..sum(a)=53, need 6 bits (max 63). Use 6 ancilla qubits as accumulator.
    acc = ancilla_qubits[:6]  # 6-bit register holding running sum, starts |0>
    nbits = 6

    def add_constant_controlled(ctrl, c):
        # Add constant c into acc (mod 2^nbits) controlled on ctrl, using ripple carry via MCX.
        # We add c by, for each bit position, doing controlled increments.
        # Simpler: decompose c and add using controlled adder of a constant.
        # Implement addition of constant c to register acc, controlled by ctrl.
        # Use the standard "controlled increment by constant" via cascade of MCX from high bits.
        cbits = [(c >> k) & 1 for k in range(nbits)]
        for k in range(nbits):
            if cbits[k]:
                # add 1 at position k: increment subregister acc[k:]
                for j in range(nbits - 1, k, -1):
                    controls = [ctrl] + acc[k:j]
                    qc.mcx(controls, acc[j])
                qc.cx(ctrl, acc[k])

    def add_constant_controlled_inv(ctrl, c):
        cbits = [(c >> k) & 1 for k in range(nbits)]
        for k in range(nbits - 1, -1, -1):
            if cbits[k]:
                qc.cx(ctrl, acc[k])
                for j in range(k + 1, nbits):
                    controls = [ctrl] + acc[k:j]
                    qc.mcx(controls, acc[j])

    # Compute the sum into acc
    for i in range(n):
        add_constant_controlled(problem_qubits[i], a[i])

    # Phase: -1 iff acc == T. Flip acc bits so target maps to all-ones, MCP(pi), unflip.
    tbits = [(T >> k) & 1 for k in range(nbits)]
    for k in range(nbits):
        if tbits[k] == 0:
            qc.x(acc[k])
    qc.mcp(np.pi, acc[:-1], acc[-1])
    for k in range(nbits):
        if tbits[k] == 0:
            qc.x(acc[k])

    # Uncompute the sum
    for i in range(n - 1, -1, -1):
        add_constant_controlled_inv(problem_qubits[i], a[i])
