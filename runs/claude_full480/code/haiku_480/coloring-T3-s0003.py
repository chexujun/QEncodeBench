from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0,1), (0,2), (0,3), (0,4), (1,2), (1,3), (1,4)]
    
    batch1_result = ancilla_qubits[0]
    batch2_result = ancilla_qubits[1]
    combine_temp = ancilla_qubits[2]
    same_color = ancilla_qubits[2]
    su = ancilla_qubits[3]
    sv = combine_temp
    
    qc.x(batch1_result)
    qc.x(batch2_result)
    
    batch1_edges = edges[:4]
    batch2_edges = edges[4:]
    
    for u, v in batch1_edges:
        b0u, b1u = problem_qubits[2*u], problem_qubits[2*u + 1]
        b0v, b1v = problem_qubits[2*v], problem_qubits[2*v + 1]
        
        qc.cx(b0u, su)
        qc.cx(b1u, su)
        qc.cx(b0v, sv)
        qc.cx(b1v, sv)
        
        qc.x(su)
        qc.x(sv)
        qc.mcx([su, sv], same_color, mode='basic')
        qc.x(su)
        qc.x(sv)
        
        qc.x(b1u)
        qc.x(b1v)
        qc.mcx([b0u, b1u, b0v, b1v], combine_temp, mode='basic')
        qc.cx(combine_temp, same_color)
        qc.mcx([b0u, b1u, b0v, b1v], combine_temp, mode='basic')
        qc.x(b1u)
        qc.x(b1v)
        
        qc.x(b0u)
        qc.x(b0v)
        qc.mcx([b0u, b1u, b0v, b1v], combine_temp, mode='basic')
        qc.cx(combine_temp, same_color)
        qc.mcx([b0u, b1u, b0v, b1v], combine_temp, mode='basic')
        qc.x(b0u)
        qc.x(b0v)
        
        qc.cx(b0v, sv)
        qc.cx(b1v, sv)
        qc.cx(b0u, su)
        qc.cx(b1u, su)
        
        qc.mcx([batch1_result, same_color], combine_temp, mode='basic')
        qc.cx(combine_temp, batch1_result)
        qc.cx(combine_temp, batch1_result)
        qc.mcx([batch1_result, same_color], combine_temp, mode='basic')
    
    for u, v in batch2_edges:
        b0u, b1u = problem_qubits[2*u], problem_qubits[2*u + 1]
        b0v, b1v = problem_qubits[2*v], problem_qubits[2*v + 1]
        
        qc.cx(b0u, su)
        qc.cx(b1u, su)
        qc.cx(b0v, sv)
        qc.cx(b1v, sv)
        
        qc.x(su)
        qc.x(sv)
        qc.mcx([su, sv], same_color, mode='basic')
        qc.x(su)
        qc.x(sv)
        
        qc.x(b1u)
        qc.x(b1v)
        qc.mcx([b0u, b1u, b0v, b1v], combine_temp, mode='basic')
        qc.cx(combine_temp, same_color)
        qc.mcx([b0u, b1u, b0v, b1v], combine_temp, mode='basic')
        qc.x(b1u)
        qc.x(b1v)
        
        qc.x(b0u)
        qc.x(b0v)
        qc.mcx([b0u, b1u, b0v, b1v], combine_temp, mode='basic')
        qc.cx(combine_temp, same_color)
        qc.mcx([b0u, b1u, b0v, b1v], combine_temp, mode='basic')
        qc.x(b0u)
        qc.x(b0v)
        
        qc.cx(b0v, sv)
        qc.cx(b1v, sv)
        qc.cx(b0u, su)
        qc.cx(b1u, su)
        
        qc.mcx([batch2_result, same_color], combine_temp, mode='basic')
        qc.cx(combine_temp, batch2_result)
        qc.cx(combine_temp, batch2_result)
        qc.mcx([batch2_result, same_color], combine_temp, mode='basic')
    
    phase_qubit = combine_temp
    qc.mcx([batch1_result, batch2_result], phase_qubit, mode='basic')
    qc.z(phase_qubit)
    qc.mcx([batch1_result, batch2_result], phase_qubit, mode='basic')
    
    for u, v in reversed(batch2_edges):
        b0u, b1u = problem_qubits[2*u], problem_qubits[2*u + 1]
        b0v, b1v = problem_qubits[2*v], problem_qubits[2*v + 1]
        
        qc.mcx([batch2_result, same_color], combine_temp, mode='basic')
        qc.cx(combine_temp, batch2_result)
        qc.cx(combine_temp, batch2_result)
        qc.mcx([batch2_result, same_color], combine_temp, mode='basic')
        
        qc.cx(b0v, sv)
        qc.cx(b1v, sv)
        qc.cx(b0u, su)
        qc.cx(b1u, su)
        
        qc.x(b0u)
        qc.x(b0v)
        qc.mcx([b0u, b1u, b0v, b1v], combine_temp, mode='basic')
        qc.cx(combine_temp, same_color)
        qc.mcx([b0u, b1u, b0v, b1v], combine_temp, mode='basic')
        qc.x(b0u)
        qc.x(b0v)
        
        qc.x(b1u)
        qc.x(b1v)
        qc.mcx([b0u, b1u, b0v, b1v], combine_temp, mode='basic')
        qc.cx(combine_temp, same_color)
        qc.mcx([b0u, b1u, b0v, b1v], combine_temp, mode='basic')
        qc.x(b1u)
        qc.x(b1v)
        
        qc.x(su)
        qc.x(sv)
        qc.mcx([su, sv], same_color, mode='basic')
        qc.x(su)
        qc.x(sv)
        
        qc.cx(b0v, sv)
        qc.cx(b1v, sv)
        qc.cx(b0u, su)
        qc.cx(b1u, su)
    
    for u, v in reversed(batch1_edges):
        b0u, b1u = problem_qubits[2*u], problem_qubits[2*u + 1]
        b0v, b1v = problem_qubits[2*v], problem_qubits[2*v + 1]
        
        qc.mcx([batch1_result, same_color], combine_temp, mode='basic')
        qc.cx(combine_temp, batch1_result)
        qc.cx(combine_temp, batch1_result)
        qc.mcx([batch1_result, same_color], combine_temp, mode='basic')
        
        qc.cx(b0v, sv)
        qc.cx(b1v, sv)
        qc.cx(b0u, su)
        qc.cx(b1u, su)
        
        qc.x(b0u)
        qc.x(b0v)
        qc.mcx([b0u, b1u, b0v, b1v], combine_temp, mode='basic')
        qc.cx(combine_temp, same_color)
        qc.mcx([b0u, b1u, b0v, b1v], combine_temp, mode='basic')
        qc.x(b0u)
        qc.x(b0v)
        
        qc.x(b1u)
        qc.x(b1v)
        qc.mcx([b0u, b1u, b0v, b1v], combine_temp, mode='basic')
        qc.cx(combine_temp, same_color)
        qc.mcx([b0u, b1u, b0v, b1v], combine_temp, mode='basic')
        qc.x(b1u)
        qc.x(b1v)
        
        qc.x(su)
        qc.x(sv)
        qc.mcx([su, sv], same_color, mode='basic')
        qc.x(su)
        qc.x(sv)
        
        qc.cx(b0v, sv)
        qc.cx(b1v, sv)
        qc.cx(b0u, su)
        qc.cx(b1u, su)
    
    qc.x(batch2_result)
    qc.x(batch1_result)
