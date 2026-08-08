import numpy as np, statistics
from pathlib import Path
PAT=Path('/work/dataset/patterns')
names=[]; protos=[]; embs={}
for d in sorted(PAT.iterdir()):
    if (d/'prototype.npy').exists() and (d/'embeddings.npy').exists():
        e=np.load(d/'embeddings.npy').astype('float32')
        if len(e)<5: continue
        names.append(d.name); protos.append(np.load(d/'prototype.npy').astype('float32')); embs[d.name]=e
M=np.stack(protos); idx={n:i for i,n in enumerate(names)}
rows=[]
for n in names:
    e=embs[n]; sims=e@M.T; pred=sims.argmax(1)
    acc=(pred==idx[n]).mean()
    wrong=pred[pred!=idx[n]]; conf=''
    if len(wrong):
        v,c=np.unique(wrong,return_counts=True); j=v[c.argmax()]; conf='%s (%d%%)'%(names[j],round(100*c.max()/len(e)))
    rows.append((acc,len(e),n,conf))
rows.sort()
print('=== %d especies evaluadas | PEORES 22 ==='%len(rows))
for acc,n,name,conf in rows[:22]:
    print('%3d%% | %4d img | %-26s | conf: %s'%(round(acc*100),n,name[:26],conf))
low=[r for r in rows if r[0]<0.8]; hi=[r for r in rows if r[0]>=0.8]
print('\n<80%%: %d/%d (%d%%)'%(len(low),len(rows),round(100*len(low)/len(rows))))
print('mediana imgs  <80%%: %d   |  >=80%%: %d'%(statistics.median([r[1] for r in low]) if low else 0, statistics.median([r[1] for r in hi]) if hi else 0))
# ¿la confusión es mutua entre especies del MISMO género? (lookalikes)
same_genus=sum(1 for a,n,nm,cf in low if cf and cf.split('_')[0]==nm.split('_')[0])
print('de las <80%%, confundidas con especie del MISMO género: %d/%d'%(same_genus,len(low)))
