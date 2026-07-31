```python
def build_oracle(qc):
    q = list(range(10))
    a0, phase, a2, eq23, eq04 = 10, 11, 12, 13, 14
    def xor_term(controls, values, target):
        neg=[c for c,v in zip(controls,values) if not v]
        for c in neg: qc.x(c)
        qc.mcx(controls,target)
        for c in reversed(neg): qc.x(c)
    def phase_term(controls, values):
        neg=[c for c,v in zip(controls,values) if not v]
        for c in neg: qc.x(c)
        qc.x(phase);qc.h(phase);qc.mcx(controls,phase);qc.h(phase);qc.x(phase)
        for c in reversed(neg): qc.x(c)
    qc.cx(0,a0);qc.cx(1,a0);qc.cx(4,a2);qc.cx(5,a2)
    xor_term([a2,6,7],[0,0,0],eq23);xor_term([a2,6,7],[0,1,1],eq23);xor_term([4,5,6,7],[0,1,0,1],eq23);xor_term([4,5,6,7],[1,0,1,0],eq23)
    xor_term([a0,8,9],[0,0,0],eq04);xor_term([a0,8,9],[0,1,1],eq04);xor_term([0,1,8,9],[0,1,0,1],eq04);xor_term([0,1,8,9],[1,0,1,0],eq04)
    common=[eq23,eq04]
    phase_term([a0,4,5,2,3]+common,[0,0,1,1,0,1,1]);phase_term([a0,4,5,2,3]+common,[0,1,0,0,1,1,1])
    phase_term([0,1,a2,2,3]+common,[0,1,0,1,0,1,1]);phase_term([0,1,a2,2,3]+common,[1,0,0,0,1,1,1])
    phase_term([0,1,4,5,2,3]+common,[0,1,1,0,0,0,1,1]);phase_term([0,1,4,5,2,3]+common,[1,0,0,1,0,0,1,1])
    phase_term([0,1,4,5,2,3]+common,[0,1,1,0,1,1,1,1]);phase_term([0,1,4,5,2,3]+common,[1,0,0,1,1,1,1,1])
    xor_term([0,1,8,9],[1,0,1,0],eq04);xor_term([0,1,8,9],[0,1,0,1],eq04);xor_term([a0,8,9],[0,1,1],eq04);xor_term([a0,8,9],[0,0,0],eq04)
    xor_term([4,5,6,7],[1,0,1,0],eq23);xor_term([4,5,6,7],[0,1,0,1],eq23);xor_term([a2,6,7],[0,1,1],eq23);xor_term([a2,6,7],[0,0,0],eq23)
    qc.cx(5,a2);qc.cx(4,a2);qc.cx(1,a0);qc.cx(0,a0)
```
