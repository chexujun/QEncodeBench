from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    x0, x1, x2, x3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]
    edges = [(x0, x3), (x1, x2), (x2, x3)]

    e_anc = ancilla_qubits[0:3]   # one ancilla per edge (edge covered)
    c_flag = ancilla_qubits[3]    # count(x) <= 2 flag
    result = ancilla_qubits[4]    # final predicate
    tmp = ancilla_qubits[5]       # scratch for counting

    def compute():
        # --- edge coverage: e_anc[i] = 1 iff edge i covered (u OR v) ---
        for i, (u, v) in enumerate(edges):
            a = e_anc[i]
            qc.x(u)
            qc.x(v)
            qc.ccx(u, v, a)
            qc.x(a)          # a = NOT(NOT u AND NOT v) = u OR v
            qc.x(u)
            qc.x(v)

        # --- count of 1-bits <= 2  <=>  NOT all-four-set AND NOT(exactly three set)?
        # size<=2 means: number of ones is 0,1, or 2.  Equivalent: NOT(>=3 ones).
        # >=3 ones means at least one of the C(4,3)=4 triples is all-ones, OR all four.
        # Simpler: >=3 ones iff at least 3 of the 4 bits are 1.
        # We set c_flag = 1 iff NOT(>=3 ones).
        # Compute "at least 3 ones" into tmp via the 4 triples (all-ones of a triple implies >=3).
        # If >=3 ones, exactly one or (for 4) multiple triples fire; we OR them into tmp.
        triples = [(x0, x1, x2), (x0, x1, x3), (x0, x2, x3), (x1, x2, x3)]
        # tmp accumulates OR of triple-AND terms. Use controlled toggles guarded so OR (not XOR miscount):
        # For OR of possibly-multiple terms we cannot simple-XOR. Instead detect >=3 by:
        # >=3 ones  <=>  sum>=3. The set of x with sum>=3: {1110,1101,1011,0111,1111}.
        # Note 1111 makes all four triples true (even count->XOR=0). So XOR of triple-ANDs is unreliable.
        # Use a cleaner route: c_flag = 1 iff at most two ones = NOT(t3) where t3 = "three or more".
        # Compute t3 with mcx over each triple but guard against double counting using tmp as OR via
        # compute-into-fresh then combine. We do OR of 5 explicit >=3 states through triples with 1111 handled.
        # Set tmp=1 if any triple all-ones:
        for (a, b, c) in triples:
            qc.mcx([a, b, c], tmp, mode='noancilla')  # XOR-accumulate
        # For 1111 all four triples fire -> XOR gives 0; fix by toggling tmp when all four set:
        qc.mcx([x0, x1, x2, x3], tmp, mode='noancilla')  # add 1 -> now odd count 4+1=5 -> tmp=1
        # Now tmp = 1 for all sum>=3 states:
        #   sum==3: exactly one triple -> XOR=1, plus four-set term=0 -> 1  (good)
        #   sum==4: four triples XOR=0, plus four-set term=1 -> 1          (good)
        #   sum<=2: no triple, no four -> 0                                (good)
        qc.x(tmp)  # c_flag source: tmp now =1 iff sum<=2
        qc.cx(tmp, c_flag)
        qc.x(tmp)  # restore tmp to its >=3 value for later uncompute

        # --- result = AND(all edges covered) AND c_flag ---
        qc.mcx([e_anc[0], e_anc[1], e_anc[2], c_flag], result, mode='noancilla')

    compute()
    qc.z(result)

    # uncompute (exact mirror)
    qc.mcx([e_anc[0], e_anc[1], e_anc[2], c_flag], result, mode='noancilla')

    qc.x(tmp)
    qc.cx(tmp, c_flag)
    qc.x(tmp)
    qc.mcx([x0, x1, x2, x3], tmp, mode='noancilla')
    triples = [(x0, x1, x2), (x0, x1, x3), (x0, x2, x3), (x1, x2, x3)]
    for (a, b, c) in triples:
        qc.mcx([a, b, c], tmp, mode='noancilla')

    for i in range(len(edges) - 1, -1, -1):
        u, v = edges[i]
        a = e_anc[i]
        qc.x(u)
        qc.x(v)
        qc.x(a)
        qc.ccx(u, v, a)
        qc.x(u)
        qc.x(v)
