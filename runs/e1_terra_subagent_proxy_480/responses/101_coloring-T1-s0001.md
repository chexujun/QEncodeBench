```python
def build_oracle(qc):
    def mark_equal(a,b,c,d,target):
        qc.x(target);qc.cx(a,target);qc.cx(b,target);qc.cx(c,target);qc.cx(d,target);qc.ccx(a,d,target);qc.ccx(b,c,target);qc.mcx([b,c,d],target);qc.mcx([a,b,d],target);qc.mcx([a,c,d],target);qc.mcx([a,b,c],target)
    edges=((0,1),(2,3),(2,4),(3,4));flags=(10,11,12,13)
    for (u,v),flag in zip(edges,flags):mark_equal(2*u,2*u+1,2*v,2*v+1,flag)
    for flag in flags:qc.x(flag)
    qc.mcp(3.141592653589793,list(flags[:3]),flags[3])
    for flag in reversed(flags):qc.x(flag)
    for (u,v),flag in reversed(tuple(zip(edges,flags))):mark_equal(2*u,2*u+1,2*v,2*v+1,flag)
```
