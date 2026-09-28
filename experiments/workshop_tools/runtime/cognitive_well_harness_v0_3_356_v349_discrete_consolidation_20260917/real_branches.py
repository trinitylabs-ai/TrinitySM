"""Bounded real branch proofs with independent exact witness replay.

Discovery may split a polynomial equation into all its factor-zero branches,
use a sum-of-squares equality, or close a branch by an ideal identity or a
contradiction with admitted real conditions. Unknown branches are never dropped.
No problem data, source-name dispatch, numerical roots, or model calls are used.
"""
from __future__ import annotations

import itertools
import re
import sympy as sp

from . import radical_certificate as radical, sum_of_squares as squares
from cognitive_well_harness_v0_3_282_unit_circle_laurent_elimination_20260905.symbol_safety import FreshNames

SCHEMA = 'checked-real-polynomial-branches-v1'
MAX_SYMBOLS = 16
MAX_EQUATIONS = 64
MAX_CONDITIONS = 256
MAX_TERMS = 2048
MAX_DEGREE = 32
MAX_PRODUCT_WORK = 50000
MAX_NODES = 31
MAX_DEPTH = 5
MAX_REDUCTIONS = 512
MAX_DERIVED = 8
MAX_SIGN_FACTS = 24
MAX_SIGN_PAIRS = 64
MAX_RENDERED_CHARACTERS = 120000


class BoundExceeded(ValueError):
    pass


class Context:
    def __init__(self, system):
        names = system.get('symbols')
        if (not isinstance(names,list) or not 1 <= len(names) <= MAX_SYMBOLS
                or len(set(names)) != len(names)
                or any(not isinstance(n,str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,47}',n) for n in names)):
            raise ValueError('real certificate requires bounded unique scalar names')
        self.symbols = [sp.Symbol(n,real=True) for n in names]
        generators, guards = system.get('generators'), system.get('guards')
        if (not isinstance(generators,dict) or not 1 <= len(generators) <= MAX_EQUATIONS
                or not isinstance(guards,dict) or len(guards) > MAX_CONDITIONS):
            raise ValueError('invalid real certificate equations/guards')
        self.equations = [self.decode(generators[key]) for key in sorted(generators)]
        self.target = self.decode(system['target'])
        self.conditions = []
        raw = system.get('real_conditions',[])
        if not isinstance(raw,list) or len(raw)>MAX_CONDITIONS:
            raise ValueError('invalid real condition list')
        for row in raw:
            if (not isinstance(row,dict) or set(row)!={'label','relation','polynomial'}
                    or not isinstance(row['label'],str) or row['relation'] not in {'gt','ge','ne'}):
                raise ValueError('invalid real condition')
            self.conditions.append((row['relation'],self.decode(row['polynomial']),row['label']))
        self.nonzeros = [(self.decode(guards[label]),label) for label in sorted(guards)]
        self.nonzeros += [(value,label) for relation,value,label in self.conditions if relation=='ne']
        self.system_hash = radical.backends.division.exact_tools.stable_hash(system)

    def poly(self,value):
        p = sp.Poly(value,*self.symbols,domain=sp.QQ)
        if len(p.terms()) > MAX_TERMS or p.total_degree() > MAX_DEGREE:
            raise BoundExceeded('real polynomial size bound')
        return p

    def clean(self,value):
        return self.poly(value).as_expr()

    def mul(self,a,b):
        pa,pb = self.poly(a),self.poly(b)
        if len(pa.terms())*len(pb.terms()) > MAX_PRODUCT_WORK:
            raise BoundExceeded('real polynomial multiplication bound')
        return self.clean(pa*pb)

    def encode(self,value):
        return radical.laurent._payload(self.clean(value),self.symbols)

    def decode(self,payload):
        terms = payload.get('terms') if isinstance(payload,dict) else None
        if not isinstance(terms,list) or len(terms)>MAX_TERMS:
            raise ValueError('invalid real polynomial terms')
        result = {}
        for row in terms:
            if not isinstance(row,dict):raise ValueError('invalid real polynomial term')
            powers, coefficient = row.get('powers'),row.get('coefficient')
            if (not isinstance(powers,list) or len(powers)!=len(self.symbols)
                    or any(type(p) is not int or p<0 for p in powers)
                    or sum(powers)>MAX_DEGREE or tuple(powers) in result
                    or not isinstance(coefficient,dict)
                    or set(coefficient)!={'real_numerator','real_denominator','imaginary_numerator','imaginary_denominator'}
                    or any(type(v) is not int for v in coefficient.values())
                    or coefficient['real_denominator']<=0 or coefficient['imaginary_denominator']<=0
                    or coefficient['imaginary_numerator']!=0):
                raise ValueError('real certificate requires exact rational polynomial terms')
            result[tuple(powers)] = sp.Rational(coefficient['real_numerator'],coefficient['real_denominator'])
        return self.poly(sp.Poly.from_dict(result,self.symbols,domain=sp.QQ)).as_expr()

    def identity(self,value,encoded,equations,remainder=sp.Integer(0)):
        if not isinstance(encoded,list) or len(encoded)!=len(equations):
            raise ValueError('real certificate multiplier count mismatch')
        multipliers = [self.decode(p) for p in encoded]
        total = remainder
        for q,e in zip(multipliers,equations,strict=True):
            total = self.clean(total+self.mul(q,e))
        if self.clean(value-total)!=0:
            raise ValueError('real certificate identity replay failed')
        return multipliers


def rational(text):
    if not isinstance(text,str) or len(text)>1024 or not re.fullmatch(r'-?\d+(?:/[1-9]\d*)?',text):
        raise ValueError('invalid exact real certificate weight')
    return sp.Rational(text)


def replay(system,certificate):
    """Check identities/tree coverage only. Never rerun factor or proof search."""
    ctx = Context(system)
    if (not isinstance(certificate,dict) or set(certificate)!={'schema','system_sha256','tree'}
            or certificate['schema']!=SCHEMA or certificate['system_sha256']!=ctx.system_hash):
        raise ValueError('real branch certificate source binding mismatch')
    count = 0
    def visit(node,equations,depth):
        nonlocal count
        count += 1
        if count>MAX_NODES or depth>MAX_DEPTH or len(equations)>MAX_EQUATIONS+MAX_DEPTH*32:
            raise ValueError('real branch certificate tree bound')
        if not isinstance(node,dict):raise ValueError('invalid real branch node')
        kind = node.get('kind')
        if kind=='target':
            if set(node)!={'kind','multipliers'}:raise ValueError('invalid target leaf')
            ctx.identity(ctx.target,node['multipliers'],equations)
        elif kind=='nonzero_contradiction':
            if set(node)!={'kind','index','multipliers'}:raise ValueError('invalid nonzero leaf')
            index=node['index']
            if type(index) is not int or not 0<=index<len(ctx.nonzeros):raise ValueError('invalid nonzero index')
            ctx.identity(ctx.nonzeros[index][0],node['multipliers'],equations)
        elif kind=='sign_contradiction':
            if set(node)!={'kind','combination','multipliers','remainder','nonpositive'}:
                raise ValueError('invalid sign leaf')
            combination=node['combination']
            if not isinstance(combination,list) or not 1<=len(combination)<=MAX_SIGN_FACTS:
                raise ValueError('invalid sign combination')
            value=sp.Integer(0);strict=False;seen=set()
            for row in combination:
                if not isinstance(row,dict) or set(row)!={'index','weight'}:raise ValueError('invalid sign term')
                index=row['index'];weight=rational(row['weight'])
                if type(index) is not int or not 0<=index<len(ctx.conditions) or index in seen or weight<=0:
                    raise ValueError('invalid sign weight/index')
                seen.add(index);relation,source,_=ctx.conditions[index]
                if relation not in {'gt','ge'}:raise ValueError('nonzero is not a sign')
                value=ctx.clean(value+weight*source);strict |= relation=='gt'
            remainder=ctx.decode(node['remainder'])
            ctx.identity(value,node['multipliers'],equations,remainder)
            if node['nonpositive'] is None:
                if remainder!=0 or not strict:raise ValueError('weak zero is not a contradiction')
            else:
                forms=squares.replay(node['nonpositive'],-remainder,ctx.symbols)
                if not strict and not any(not f.free_symbols and f!=0 for f in forms):
                    raise ValueError('weak sign requires a strictly negative remainder')
        elif kind in {'split','squares'}:
            required={'kind','equation','multipliers'}|({'coefficient','factors','children'} if kind=='split' else {'decomposition','child'})
            if set(node)!=required:raise ValueError('invalid branch node fields')
            value=ctx.decode(node['equation'])
            ctx.identity(value,node['multipliers'],equations)
            if kind=='squares':
                forms=squares.replay(node['decomposition'],value,ctx.symbols)
                visit(node['child'],equations+forms,depth+1)
            else:
                coefficient=rational(node['coefficient']);factors=node['factors'];children=node['children']
                if coefficient==0 or not isinstance(factors,list) or not 1<=len(factors)<=8 or not isinstance(children,list) or len(children)!=len(factors):
                    raise ValueError('branch coverage incomplete')
                product=coefficient;decoded=[]
                for row in factors:
                    if not isinstance(row,dict) or set(row)!={'polynomial','exponent'}:raise ValueError('invalid factor')
                    f=ctx.decode(row['polynomial']);power=row['exponent']
                    if not f.free_symbols or type(power) is not int or not 1<=power<=MAX_DEGREE:
                        raise ValueError('invalid factor/exponent')
                    decoded.append(f)
                    for _ in range(power):product=ctx.mul(product,f)
                if ctx.clean(value-product)!=0:raise ValueError('factorization identity replay failed')
                for f,child in zip(decoded,children,strict=True):visit(child,equations+[f],depth+1)
        else:
            raise ValueError('unresolved or unknown branch cannot certify a target')
    visit(certificate['tree'],ctx.equations,0)
    return {'verified':True,'conditional_target_proved':True,'real_conditions_preserved':True,
            'system_sha256':ctx.system_hash,'certificate_sha256':radical.backends.division.exact_tools.stable_hash(certificate),
            'proof_nodes':count,'identity':'complete_real_branch_tree_with_exact_polynomial_identities'}


class Search:
    def __init__(self,ctx):
        self.ctx=ctx
        self.stats={'visited_nodes':0,'reductions':0,'closed_targets':0,'closed_contradictions':0,'splits':0,'squares':0,'unresolved_branches':0}

    def reduce(self,value,basis):
        self.stats['reductions']+=1
        if self.stats['reductions']>MAX_REDUCTIONS:raise BoundExceeded('real branch reduction budget')
        if not basis:return [],self.ctx.clean(value)
        if value==0:return [sp.Integer(0)]*len(basis[0][1]),sp.Integer(0)
        q,r=sp.reduced(value,[b[0] for b in basis],*self.ctx.symbols,domain=sp.QQ)
        out=[sp.Integer(0)]*len(basis[0][1])
        for quotient,(_,weights) in zip(q,basis,strict=True):
            for i,weight in enumerate(weights):
                out[i]=self.ctx.clean(out[i]+self.ctx.mul(quotient,weight))
        return out,self.ctx.clean(r)

    def encoded(self,weights):return [self.ctx.encode(w) for w in weights]

    def basis(self,equations):
        result=[]
        for i,equation in enumerate(equations):
            if equation==0:continue
            lc=self.ctx.poly(equation).LC()
            row=[sp.Integer(0)]*len(equations);row[i]=1/lc
            result.append((self.ctx.clean(equation/lc),row))
        return result

    def contradictions(self,basis,equations):
        candidates=[(i,r,v) for i,(r,v,_) in enumerate(self.ctx.conditions) if r in {'gt','ge'}]
        candidates.sort(key=lambda item:(self.ctx.poly(item[2]).total_degree(),len(self.ctx.poly(item[2]).terms()),item[0]))
        reduced=[]
        for index,relation,value in candidates[:MAX_SIGN_FACTS]:
            q,r=self.reduce(value,basis)
            if not basis:q=[sp.Integer(0)]*len(equations)
            reduced.append((index,relation,q,r))
        combinations=[[(row,sp.Integer(1))] for row in reduced]
        for a,b in itertools.islice(itertools.combinations(reduced,2),MAX_SIGN_PAIRS):
            combinations.extend([[(a,sp.Integer(1)),(b,weight)] for weight in (sp.Integer(1),sp.Integer(2),sp.Rational(1,2))])
        for combination in combinations:
            r=self.ctx.clean(sum(weight*row[3] for row,weight in combination))
            strict=any(row[1]=='gt' for row,weight in combination)
            decomposition=None if r==0 else squares.quadratic(-r,self.ctx.symbols)
            if r==0:
                if not strict:continue
            elif decomposition is None:continue
            elif not strict:
                forms=squares.replay(decomposition,-r,self.ctx.symbols)
                if not any(not f.free_symbols and f!=0 for f in forms):continue
            q=[self.ctx.clean(sum(weight*row[2][j] for row,weight in combination)) for j in range(len(equations))]
            return {'kind':'sign_contradiction','combination':[{'index':row[0],'weight':str(weight)} for row,weight in combination],
                    'multipliers':self.encoded(q),'remainder':self.ctx.encode(r),'nonpositive':decomposition}
        for index,(value,_) in enumerate(self.ctx.nonzeros):
            q,r=self.reduce(value,basis)
            if r==0:
                return {'kind':'nonzero_contradiction','index':index,'multipliers':self.encoded(q or [sp.Integer(0)]*len(equations))}
        return None

    def extend(self,basis):
        """A bounded batch of exact S-polynomial consequences, with identities."""
        ctx=self.ctx
        pairs=list(itertools.combinations(range(len(basis)),2))
        pairs.sort(key=lambda ij:sum(len(ctx.poly(basis[i][0]).terms()) for i in ij))
        for i,j in pairs[:MAX_DERIVED]:
            pa,pb=ctx.poly(basis[i][0]),ctx.poly(basis[j][0])
            ma,mb=pa.monoms()[0],pb.monoms()[0]
            common=[max(a,b) for a,b in zip(ma,mb)]
            left=sp.prod(s**(c-a) for s,c,a in zip(ctx.symbols,common,ma))/pa.LC()
            right=sp.prod(s**(c-b) for s,c,b in zip(ctx.symbols,common,mb))/pb.LC()
            value=ctx.clean(ctx.mul(left,pa.as_expr())-ctx.mul(right,pb.as_expr()))
            q,r=self.reduce(value,basis)
            if r==0:continue
            weights=[ctx.clean(ctx.mul(left,a)-ctx.mul(right,b)-c) for a,b,c in zip(basis[i][1],basis[j][1],q,strict=True)]
            lc=ctx.poly(r).LC()
            basis.append((ctx.clean(r/lc),[ctx.clean(w/lc) for w in weights]))

    def node(self,equations,depth=0,used=frozenset()):
        self.stats['visited_nodes']+=1
        if self.stats['visited_nodes']>MAX_NODES or depth>MAX_DEPTH:
            self.stats['unresolved_branches']+=1;return None
        ctx=self.ctx;basis=self.basis(equations)
        q,r=self.reduce(ctx.target,basis)
        if r==0:
            self.stats['closed_targets']+=1
            return {'kind':'target','multipliers':self.encoded(q or [sp.Integer(0)]*len(equations))}
        contradiction=self.contradictions(basis,equations)
        if contradiction:
            self.stats['closed_contradictions']+=1;return contradiction
        for pass_index in range(2):
            if pass_index:
                self.extend(basis)
                q,r=self.reduce(ctx.target,basis)
                if r==0:
                    self.stats['closed_targets']+=1
                    return {'kind':'target','multipliers':self.encoded(q)}
                contradiction=self.contradictions(basis,equations)
                if contradiction:
                    self.stats['closed_contradictions']+=1;return contradiction
            options=[]
            for value,weights in basis:
                key=sp.srepr(ctx.poly(value).monic().as_expr())
                if key in used:continue
                for sign in (1,-1):
                    decomposition=squares.quadratic(sign*value,ctx.symbols)
                    if decomposition is not None:
                        forms=squares.replay(decomposition,sign*value,ctx.symbols)
                        if all(any(ctx.clean(f-e)==0 or ctx.clean(f+e)==0 for e in equations) for f in forms):continue
                        child=self.node(equations+forms,depth+1,used|{key})
                        self.stats['squares']+=1
                        if child is None:return None
                        return {'kind':'squares','equation':ctx.encode(sign*value),
                                'multipliers':self.encoded([sign*w for w in weights]),'decomposition':decomposition,'child':child}
                coefficient,factors=sp.factor_list(value,*ctx.symbols)
                if not 1<=len(factors)<=8 or (len(factors)==1 and factors[0][1]==1):continue
                options.append((sum(ctx.poly(f).total_degree() for f,n in factors),len(factors),key,value,weights,coefficient,factors))
            if options:
                _,_,key,value,weights,coefficient,factors=min(options,key=lambda row:row[:3])
                self.stats['splits']+=1;children=[]
                for f,power in factors:
                    child=self.node(equations+[f],depth+1,used|{key})
                    if child is None:return None
                    children.append(child)
                return {'kind':'split','equation':ctx.encode(value),'multipliers':self.encoded(weights),
                        'coefficient':str(coefficient),'factors':[{'polynomial':ctx.encode(f),'exponent':int(n)} for f,n in factors],
                        'children':children}
        self.stats['unresolved_branches']+=1
        return None


def solve(system):
    ctx=Context(system);search=Search(ctx)
    try:
        tree=search.node(ctx.equations)
    except BoundExceeded as error:
        return {'verified':False,'verdict':'INCONCLUSIVE','reason':str(error),'statistics':search.stats}
    if tree is None:
        return {'verified':False,'verdict':'INCONCLUSIVE','reason':'unresolved real branches','statistics':search.stats}
    certificate={'schema':SCHEMA,'system_sha256':ctx.system_hash,'tree':tree}
    checked=replay(system,certificate)
    return {**checked,'certificate':certificate,'statistics':search.stats}


def render(system,certificate):
    """Render every checked identity and every branch, including inequalities."""
    checked=replay(system,certificate);ctx=Context(system);names=FreshNames(ctx.symbols)
    target_label=names.take('T');condition_names=[names.take(f'S_{i+1}') for i in range(len(ctx.conditions))]
    equation_names=[names.take(f'E_{i+1}') for i in range(len(ctx.equations))]
    latex=sp.latex;lines=['## Exact proof over the real numbers']
    for label,value in zip(equation_names,ctx.equations):lines.append(r'\['+latex(label)+'='+latex(value)+'=0.\\]')
    for label,(relation,value,_) in zip(condition_names,ctx.conditions):
        op={'gt':'>','ge':r'\ge','ne':r'\ne'}[relation]
        lines.append(r'\['+latex(label)+'='+latex(value)+op+'0.\\]')
    for value,_ in ctx.nonzeros:lines.append(r'\['+latex(value)+r'\ne0.\]')
    lines.append(r'We prove \('+latex(target_label)+'='+latex(ctx.target)+r'=0\).')
    def combo(payloads,labels):
        return ' + '.join('('+latex(ctx.decode(q))+')'+latex(e) for q,e in zip(payloads,labels) if ctx.decode(q)!=0) or '0'
    def walk(node,labels,depth):
        kind=node['kind']
        if kind=='target':lines.append(r'\['+latex(target_label)+'='+combo(node['multipliers'],labels)+'=0.\\]')
        elif kind=='nonzero_contradiction':
            value=ctx.nonzeros[node['index']][0]
            lines.append(r'The nonzero assumption contradicts \['+latex(value)+'='+combo(node['multipliers'],labels)+'=0.\\]')
        elif kind=='sign_contradiction':
            expression=' + '.join('('+row['weight']+')'+latex(condition_names[row['index']]) for row in node['combination'])
            lines.append(r'For the indicated positive rational combination of sign conditions, \['+expression+'='+combo(node['multipliers'],labels)+'+('+latex(ctx.decode(node['remainder']))+').\\]')
            if node['nonpositive'] is not None:
                receipt=node['nonpositive']
                decomposition=' + '.join('('+item['weight']+')('+latex(squares.decode(item['form'],ctx.symbols))+')^2' for item in receipt['squares'])
                lines.append(r'\['+latex(-ctx.decode(node['remainder']))+'='+decomposition+'.\\]')
            lines.append('On this branch the equations vanish. The displayed identities contradict the stated strict or weak sign conditions: the combination is strictly positive and the remainder is nonpositive, or the combination is nonnegative and the remainder is strictly negative.')
        else:
            value=ctx.decode(node['equation'])
            lines.append(r'\['+latex(value)+'='+combo(node['multipliers'],labels)+'=0.\\]')
            if kind=='squares':
                forms=squares.replay(node['decomposition'],value,ctx.symbols)
                decomposition=' + '.join('('+item['weight']+')('+latex(squares.decode(item['form'],ctx.symbols))+')^2' for item in node['decomposition']['squares'])
                lines.append(r'\['+latex(value)+'='+decomposition+'.\\] Every square must vanish over the real numbers.')
                new=[names.take('F') for f in forms]
                for label,f in zip(new,forms):lines.append(r'\['+latex(label)+'='+latex(f)+'=0.\\]')
                walk(node['child'],labels+new,depth+1)
            else:
                factors=[ctx.decode(row['polynomial']) for row in node['factors']]
                product=''.join('('+latex(f)+')^{'+str(row['exponent'])+'}' for f,row in zip(factors,node['factors']))
                lines.append(r'\['+latex(value)+'=('+node['coefficient']+')'+product+'.\\] At least one factor vanishes. The following cases cover every possibility.')
                for i,(f,child) in enumerate(zip(factors,node['children']),1):
                    label=names.take('F')
                    lines.append('Case '+str(i)+' at depth '+str(depth)+r': \['+latex(label)+'='+latex(f)+'=0.\\]')
                    walk(child,labels+[label],depth+1)
    walk(certificate['tree'],equation_names,0)
    lines.append('Every case proves the target or contradicts the real hypotheses, so the target vanishes.')
    markdown='\n\n'.join(lines)
    if len(markdown)>MAX_RENDERED_CHARACTERS:raise ValueError('real branch rendering limit')
    return markdown,{**checked,'markdown':markdown,'target_label_latex':latex(target_label),'real_branch_derivation_supplied':True}
