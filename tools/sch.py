# Minimal KiCad 10 schematic layout helper: pin geometry, fields, wires, junctions, labels, checks.
import re, uuid, math
U=lambda: str(uuid.uuid4())
G=1.27
def r2(v): return round(v+0.0,2)
def P(x,y): return (r2(x),r2(y))

def tokenize(s):
    i=0;n=len(s)
    while i<n:
        c=s[i]
        if c in '()': yield c; i+=1
        elif c.isspace(): i+=1
        elif c=='"':
            j=i+1
            while s[j]!='"':
                j+= 2 if s[j]=='\\' else 1
            yield s[i:j+1]; i=j+1
        else:
            j=i
            while j<n and not s[j].isspace() and s[j] not in '()': j+=1
            yield s[i:j]; i=j
def parse(s):
    st=[[]]
    for t in tokenize(s):
        if t=='(': st.append([])
        elif t==')': x=st.pop(); st[-1].append(x)
        else: st[-1].append(t.strip('"') if t.startswith('"') else t)
    return st[0][0]
def find(node,key): return [c for c in node if isinstance(c,list) and c and c[0]==key]
def block_end(s,i):
    d=0;q=False;k=i
    while k<len(s):
        c=s[k]
        if c=='"' and s[k-1]!='\\': q=not q
        elif not q:
            if c=='(': d+=1
            elif c==')':
                d-=1
                if d==0: return k+1
        k+=1
    raise ValueError('unbalanced block at %d'%i)

class Sheet:
    def __init__(s,path):
        s.path=path; s.txt=open(path,encoding='utf-8').read()
        s.wires=[]; s.extra=[]; s.nc=[]; s.labels=[]   # labels: (kind,name,x,y,angle,shape)
        s._libpins()
        s._insts()
    def _libpins(s):
        i=s.txt.index('(lib_symbols'); e=block_end(s.txt,i)
        tree=parse(s.txt[i:e]); s.lib={}; s.libunit={}
        for sym in find(tree,'symbol'):
            name=sym[1]; pins={}
            def walk(n,unit=0):
                for c in n:
                    if isinstance(c,list) and c:
                        if c[0]=='pin':
                            at=find(c,'at')[0]; num=find(c,'number')[0][1]; nm=find(c,'name')[0][1]
                            pins.setdefault(num,[]).append((float(at[1]),float(at[2]),c[1],nm))
                            units[num]=unit
                        elif c[0]=='symbol': walk(c,int(c[1].rsplit('_',2)[1]))
            units={}; walk(sym); s.lib[name]=pins; s.libunit[name]=units
    def _insts(s):
        s.inst={}
        for m in re.finditer(r'\(symbol \(lib_id "([^"]+)"\) \(at ([\d.\-]+) ([\d.\-]+) (\d+)\)( \(mirror (\w)\))?',s.txt):
            st=m.start(); en=block_end(s.txt,st); blk=s.txt[st:en]
            ref=re.search(r'\(property "Reference" "([^"]+)"',blk).group(1)
            unit=int(re.search(r'\(unit (\d+)\)',blk).group(1))
            s.inst[ref if unit==1 else f'{ref}#u{unit}']=dict(lib=m.group(1),x=float(m.group(2)),y=float(m.group(3)),rot=int(m.group(4)),mir=m.group(6),unit=unit)
    def xf(s,ref,px,py):
        d=s.inst[ref]; dx,dy=px,-py
        if d['mir']=='y': dx=-dx
        if d['mir']=='x': dy=-dy
        for _ in range((d['rot']//90)%4): dx,dy=dy,-dx
        return P(d['x']+dx,d['y']+dy)
    def pin(s,ref,num):
        d=s.inst[ref]; px,py,_,_=s.lib[d['lib']][str(num)][0]; return s.xf(ref,px,py)
    def pins(s,ref):
        d=s.inst[ref]; out=[]
        for num,lst in s.lib[d['lib']].items():
            if s.libunit[d['lib']][num] not in (0,d['unit']): continue
            for px,py,typ,nm in lst: out.append((num,nm,typ,s.xf(ref,px,py)))
        return out
    # ---- edits
    def mirror(s,ref,axis='y'):
        s.txt=re.sub(r'(\(symbol \(lib_id "[^"]+"\) \(at [\d.\-]+ [\d.\-]+ \d+\))( \(unit)',r'\1 (mirror %s)\2'%axis,
            s.txt[:0]+s.txt,0) if False else s.txt
        # targeted: find the instance block by reference
        for m in re.finditer(r'\(symbol \(lib_id "[^"]+"\) \(at [\d.\-]+ [\d.\-]+ \d+\)',s.txt):
            en=block_end(s.txt,m.start()); blk=s.txt[m.start():en]
            if re.search(r'\(property "Reference" "%s"'%re.escape(ref),blk) and '(mirror' not in blk[:200]:
                s.txt=s.txt[:m.end()]+' (mirror %s)'%axis+s.txt[m.end():]; break
        s.inst[ref]['mir']=axis
    def field(s,ref,name,x,y,just=None,hide=False,ang=0):
        for m in re.finditer(r'\(symbol \(lib_id "[^"]+"\) \(at [\d.\-]+ [\d.\-]+ \d+\)',s.txt):
            st=m.start(); en=block_end(s.txt,st); blk=s.txt[st:en]
            if not re.search(r'\(property "Reference" "%s"'%re.escape(ref),blk): continue
            ps=blk.index('(property "%s"'%name); pe=block_end(blk,ps); prop=blk[ps:pe]
            head=re.match(r'\(property "%s" "(?:[^"\\]|\\.)*"'%name,prop).group(0)
            j=f' (justify {just})' if just else ''
            h=' (hide yes)' if hide else ''
            prop=f'{head} (at {r2(x)} {r2(y)} {ang}){h} (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27)){j}))'
            blk=blk[:ps]+prop+blk[pe:]; s.txt=s.txt[:st]+blk+s.txt[en:]; return
        raise KeyError(ref)
    def setval(s,ref,name,val):
        for m in re.finditer(r'\(symbol \(lib_id "[^"]+"\) \(at [\d.\-]+ [\d.\-]+ \d+\)',s.txt):
            st=m.start(); en=block_end(s.txt,st); blk=s.txt[st:en]
            if not re.search(r'\(property "Reference" "%s"'%re.escape(ref),blk): continue
            blk=re.sub(r'(\(property "%s" )"[^"]*"'%name,lambda mm: mm.group(1)+'"%s"'%val,blk,1)
            s.txt=s.txt[:st]+blk+s.txt[en:]; return
    def hide_misc(s):
        # move Footprint/Datasheet/Description to symbol origin and hide (keeps clutter off-sheet)
        for ref,d in s.inst.items():
            if '#u' in ref: continue
            for nm in ('Footprint','Datasheet','Description'):
                try: s.field(ref,nm,d['x'],d['y'],hide=True)
                except ValueError: pass
    def auto_fields(s,ref,kind):
        d=s.inst[ref]; x,y=d['x'],d['y']
        if kind=='v2':   # vertical 2-pin part, text to the right
            s.field(ref,'Reference',x+2.54,y-1.27,'left'); s.field(ref,'Value',x+2.54,y+1.27,'left')
        elif kind=='v2r':  # rotated 90 two-pin (LED/jumper/switch vertical)
            s.field(ref,'Reference',x+2.54,y-1.27,'right',ang=90); s.field(ref,'Value',x+2.54,y+1.27,'right',ang=90)
        elif kind=='gnd':
            s.field(ref,'Reference',x,y+6.35,hide=True); s.field(ref,'Value',x,y+3.81)
        elif kind=='pwr':
            s.field(ref,'Reference',x,y+3.81,hide=True); s.field(ref,'Value',x,y-3.81)
        elif kind=='flag':
            s.field(ref,'Reference',x,y-1.91,hide=True); s.field(ref,'Value',x,y-3.81)
    # ---- drawing
    def wire(s,*pts):
        pts=[P(*p) for p in pts]
        for a,b in zip(pts,pts[1:]):
            assert a[0]==b[0] or a[1]==b[1], ('diagonal',a,b)
            if a!=b: s.wires.append((a,b))
    def ncf(s,x,y): s.nc.append(P(x,y))
    def label(s,name,x,y,ang=0,kind='label',shape='bidirectional'):
        s.labels.append((kind,name,P(x,y),ang,shape))
    def text(s,t,x,y,size=1.27):
        t=t.replace('"','\\"').replace('\n','\\n')
        s.extra.append(f'(text "{t}" (exclude_from_sim no) (at {r2(x)} {r2(y)} 0) (effects (font (size {size} {size})) (justify left top)) (uuid "{U()}"))')
    # ---- connectivity
    def _split(s):
        pts=set([a for a,b in s.wires]+[b for a,b in s.wires])
        pts|=set(p for _,_,p,_,_ in s.labels)
        for ref in s.inst:
            for num,nm,typ,p in s.pins(ref): pts.add(p)
        changed=True
        while changed:
            changed=False; out=[]
            for a,b in s.wires:
                cut=None
                for p in pts:
                    if p in (a,b): continue
                    if a[0]==b[0]==p[0] and min(a[1],b[1])<p[1]<max(a[1],b[1]): cut=p;break
                    if a[1]==b[1]==p[1] and min(a[0],b[0])<p[0]<max(a[0],b[0]): cut=p;break
                if cut: out+= [(a,cut),(cut,b)]; changed=True
                else: out.append((a,b))
            s.wires=out
    def finish(s):
        s._split()
        deg={}
        for a,b in s.wires:
            for p in (a,b): deg[p]=deg.get(p,0)+1
        pinpts={}
        for ref in s.inst:
            for num,nm,typ,p in s.pins(ref): pinpts.setdefault(p,[]).append((ref,num,nm,typ))
        junc=[p for p,n in deg.items() if n+len(set((r,nn) for r,nn,_,_ in pinpts.get(p,[])))>=3 and n>=2]
        # report unconnected pins
        lab=set(p for _,_,p,_,_ in s.labels); ncs=set(s.nc)
        problems=[]
        for p,lst in pinpts.items():
            others=len(lst)
            uniq=set((r,n) for r,n,_,_ in lst)
            if p in deg or p in lab or p in ncs: continue
            if len(set(r for r,_,_,_ in lst))>=2: continue  # pin-to-pin
            for r,n,nm,typ in lst:
                if typ in ('no_connect',) : continue
                if len(uniq)>1 and len(set(r for r,_,_,_ in lst))==1: pass
                problems.append(f'UNCONNECTED {r}.{n}({nm}) at {p}')
        for p in lab|ncs:
            if p not in deg and p not in pinpts: problems.append(f'FLOATING label/nc at {p}')
        for a,b in s.wires:
            for p in (a,b):
                if deg[p]==1 and p not in pinpts and p not in lab and p not in ncs: problems.append(f'DANGLING wire end {p}')
        # crossings without junction
        H=[w for w in s.wires if w[0][1]==w[1][1]]; V=[w for w in s.wires if w[0][0]==w[1][0]]
        for h in H:
            for v in V:
                x=v[0][0]; y=h[0][1]
                if min(h[0][0],h[1][0])<x<max(h[0][0],h[1][0]) and min(v[0][1],v[1][1])<y<max(v[0][1],v[1][1]):
                    problems.append(f'CROSSING at {(x,y)}')
        out=[]
        for a,b in s.wires: out.append(f'(wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})) (stroke (width 0) (type default)) (uuid "{U()}"))')
        for p in junc: out.append(f'(junction (at {p[0]} {p[1]}) (diameter 0) (color 0 0 0 0) (uuid "{U()}"))')
        for p in s.nc: out.append(f'(no_connect (at {p[0]} {p[1]}) (uuid "{U()}"))')
        for kind,name,p,ang,shape in s.labels:
            if kind=='global':
                j='right' if ang==180 else 'left'
                out.append(f'(global_label "{name}" (shape {shape}) (at {p[0]} {p[1]} {ang}) (fields_autoplaced yes) (effects (font (size 1.27 1.27)) (justify {j})) (uuid "{U()}") (property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {p[0]} {p[1]} 0) (hide yes) (effects (font (size 1.27 1.27)))))')
            else:
                j='right bottom' if ang==180 else 'left bottom'
                out.append(f'(label "{name}" (at {p[0]} {p[1]} {ang}) (fields_autoplaced yes) (effects (font (size 1.27 1.27)) (justify {j})) (uuid "{U()}"))')
        out+=s.extra
        i=s.txt.index('(sheet_instances')
        s.txt=s.txt[:i]+'\n\t'.join(out)+'\n\t'+s.txt[i:]
        return problems,len(junc)
    def title(s,paper,title,rev,c1,c2,c3=''):
        s.txt=re.sub(r'\(paper "[^"]+"\)',f'(paper "{paper}")',s.txt,1)
        while '(title_block' in s.txt:
            i=s.txt.index('(title_block'); s.txt=s.txt[:i]+s.txt[block_end(s.txt,i):]
        tb=f'(title_block (title "{title}") (date "2026-10-21") (rev "{rev}") (company "DeVinci FabLab - reSkin") (comment 1 "{c1}") (comment 2 "{c2}") (comment 3 "{c3}"))'
        s.txt=re.sub(r'(\(paper "[^"]+"\))',lambda m: m.group(1)+'\n\t'+tb,s.txt,1)
    def save(s):
        d=0;q=False
        for k,c in enumerate(s.txt):
            if c=='"' and s.txt[k-1]!='\\': q=not q
            elif not q:
                d+= c=='('; d-= c==')'
        assert d==0, f'paren imbalance {d}'
        with open(s.path,'w',encoding='utf-8') as f: f.write(s.txt); f.truncate()
        chk=open(s.path,encoding='utf-8').read()
        assert chk.count('(kicad_sch')==1 and len(chk)==len(s.txt), 'write verification failed'
