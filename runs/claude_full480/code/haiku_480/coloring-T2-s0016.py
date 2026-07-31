from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    
    def compute_edge_validity(u: int, v: int, ancilla: int) -> None:
        """Compute whether edge (u,v) has different colors into ancilla."""
        b0_u = problem_qubits[2 * u]
        b1_u = problem_qubits[2 * u + 1]
        b0_v = problem_qubits[2 * v]
        b1_v = problem_qubits[2 * v + 1]
        
        # For each 4-bit input combination where colors differ, flip ancilla
        # Color encoding: code = b1*2 + b0; color = code % 3
        # Colors differ iff (code_u % 3) != (code_v % 3)
        different_color_combos = [
            (0, 0, 0, 1), (0, 0, 1, 0),
            (0, 1, 0, 0), (0, 1, 1, 0), (0, 1, 1, 1),
            (1, 0, 0, 0), (1, 0, 0, 1), (1, 0, 1, 1),
            (1, 1, 0, 1), (1, 1, 1, 0)
        ]
        
        for (b0_u_val, b1_u_val, b0_v_val, b1_v_val) in different_color_combos:
            controls = []
            negated = []
            
            if b0_u_val == 0:
                negated.append(b0_u)
            else:
                controls.append(b0_u)
            
            if b1_u_val == 0:
                negated.append(b1_u)
            else:
                controls.append(b1_u)
            
            if b0_v_val == 0:
                negated.append(b0_v)
            else:
                controls.append(b0_v)
            
            if b1_v_val == 0:
                negated.append(b1_v)
            else:
                controls.append(b1_v)
            
            # Negate qubits that should be in |0>
            for q in negated:
                qc.x(q)
            
            # Apply multi-controlled X to flip ancilla iff all conditions match
            all_controls = controls + negated
            qc.mcx(all_controls, ancilla)
            
            # Undo negations
            for q in negated:
                qc.x(q)
    
    edges = [(0, 2), (0, 3), (1, 2), (1, 3), (2, 4), (3, 4)]
    edge_ancillas = ancilla_qubits[:6]
    phase_ancilla = ancilla_qubits[6]
    
    # Initialize phase ancilla to |−⟩ = (|0⟩ - |1⟩)/√2
    qc.h(phase_ancilla)
    qc.z(phase_ancilla)
    
    # Compute edge validity flags
    for i, (u, v) in enumerate(edges):
        compute_edge_validity(u, v, edge_ancillas[i])
    
    # Apply multi-controlled phase: Z on phase_ancilla iff all edges valid
    qc.mcp(math.pi, edge_ancillas, phase_ancilla)
    
    # Uncompute edge flags (reverse order)
    for i, (u, v) in enumerate(reversed(edges)):
        compute_edge_validity(u, v, edge_ancillas[len(edges) - 1 - i])
