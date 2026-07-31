from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [6, 4, 3]
    T = 3
    n = len(problem_qubits)

    solutions = []
    for mask in range(1 << n):
        s = sum(a[i] for i in range(n) if (mask >> i) & 1)
        if s == T:
            solutions.append(mask)

    flag = ancilla_qubits[0]

    for mask in solutions:
        zero_bits = [problem_qubits[i] for i in range(n) if not ((mask >> i) & 1)]
        ctrls = [problem_qubits[i] for i in range(n)]
        for q in zero_bits:
            qc.x(q)
        qc.mcx(ctrls, flag)
        qc.z(flag)
        qc.mcx(ctrls, flag)
        for q in zero_bits:
            qc.x(q)
