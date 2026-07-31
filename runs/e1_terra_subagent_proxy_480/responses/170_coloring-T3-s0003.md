```python
def build_oracle(qc, q, anc):
    def toggle_all_different(a,b,c,target):
        perms=((0,1,2),(0,2,1),(1,0,2),(1,2,0),(2,0,1),(2,1,0))
        for ca,cb,cc in perms:
            controls=[];zeros=[]
            for v,color in ((a,ca),(b,cb),(c,cc)):
                x,y=q[2*v],q[2*v+1]
                if color==0: controls.append(y);zeros.append(y)
                elif color==1: controls.extend((x,y));zeros.append(x)
                else: controls.extend((x,y))
            for bit in zeros: qc.x(bit)
            qc.mcx(controls,target)
            for bit in reversed(zeros): qc.x(bit)
    for v,flag in zip((2,3,4),anc[:3]): toggle_all_different(0,1,v,flag)
    qc.mcx(list(anc[:3]),anc[3]);qc.z(anc[3]);qc.mcx(list(anc[:3]),anc[3])
    for v,flag in zip((4,3,2),reversed(anc[:3])): toggle_all_different(0,1,v,flag)
```
