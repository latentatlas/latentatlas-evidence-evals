"""R29 uses the frozen R28 differentiated formulas with a local sign anchor."""
from continuation import *
root_jets,tail_constants,tails,solve=previous.root_jets,previous.tail_constants,previous.tails,previous.solve
def produce(a,cert):
    arc=cert['arc'];params=arc['parameter_box'];vel=arc['refined_velocity'];b=cert['dual']['tight_box'];co=cert['coefficients']
    assert all(absup(x)<1 for x in vel)
    roots=cert['dual']['tight_roots'];jets=[root_jets(r['root'],params,b) for r in roots]
    S,srecords=transport(a,arc,b,roots);S[:3]=[arb(0)]*3;S[3]=co['D'];tt=tail_constants();tail=tails(tt)
    def partial(values,j):return vel[0]*values[j+1]-vel[1]*values[j+2]/4+vel[2]*values[j+4]/16-values[j+6]/64
    Sd=[partial(S,j) for j in range(4)];rhs=Sd[:3];rterms=[]
    for root,at in zip(roots,jets):
        p=at['p_jets_extended'];q=at['moment_jets_extended'];gamma=root['orientation']*at['residual_jets'][1]
        rawtau=p[4][0]-sm(b[j]*p[j+1][0] for j in range(3))
        part=at['weight_jets'][0]*vel[0]*rawtau
        terms=[2*q[j][0]*part/gamma for j in range(3)];rterms.append(terms)
        rhs=[rhs[j]+terms[j] for j in range(3)]
    rhs=[x+sym(tail['dual_rhs']) for x in rhs]
    bp,solution=solve(co['G'],rhs,cert['dual']['preconditioner']);assert all(absup(x)<10 for x in bp)
    Dp=Sd[3]-sm(b[j]*Sd[j] for j in range(3));fp=partial(arc['derivatives'],3)
    gp=arb(0);Bp=[arb(0)]*3;Gp=[[arb(0)]*3 for _ in range(3)];Rp=arb(0);records=[]
    for root,at in zip(roots,jets):
        sig=root['orientation'];q=at['moment_jets_extended'];p=at['p_jets_extended'];r=at['residual_jets']
        rawtau=p[4][0]-sm(b[j]*p[j+1][0] for j in range(3));rawprime=p[3][1]-sm(b[j]*p[j][1] for j in range(3))
        zp=(sm(bp[j]*p[j][0] for j in range(3))-vel[0]*rawtau)/rawprime
        qdot=[[partial([q[n][l] for n in range(10)],j) for l in range(4)] for j in range(4)]
        rd=[qdot[3][l]-sm(b[j]*qdot[j][l]+bp[j]*q[j][l] for j in range(3))+r[l+1]*zp for l in range(4)]
        qt=[[qdot[j][l]+q[j][l+1]*zp for l in range(2)] for j in range(3)]
        gam=sig*r[1];gamd=sig*rd[1];gp+=gamd
        bg=[sig*((qt[j][0]*r[2]+q[j][0]*rd[2])/r[1]-q[j][0]*r[2]*rd[1]/r[1]**2-qt[j][1])/3 for j in range(3)]
        gg=[[2*((qt[i][0]*q[j][0]+q[i][0]*qt[j][0])/gam-q[i][0]*q[j][0]*gamd/gam**2) for j in range(3)] for i in range(3)]
        rr=r[2]*rd[2]/(18*gam)-r[2]**2*gamd/(36*gam**2)-sig*rd[3]/60
        Bp=[Bp[j]+bg[j] for j in range(3)];Gp=[[Gp[i][j]+gg[i][j] for j in range(3)] for i in range(3)];Rp+=rr
        records.append({'index':root['index'],'root':root['root'],'orientation':sig,'jets':at,'root_velocity':zp,
          'fixed_u_moment_derivatives':qdot,'total_residual_derivatives':rd,'total_moment_derivatives':qt,
          'Gamma_prime':gamd,'B_prime':bg,'G_prime':gg,'R_prime':rr})
    gp+=sym(tail['Gamma_prime']);Bp=[x+sym(tail['B_prime_entry']) for x in Bp]
    Gp=[[x+sym(tail['G_prime_entry']) for x in row] for row in Gp];Rp+=sym(tail['R_prime'])
    v=co['v'];Pp=sm(Bp[j]*v[j] for j in range(3))-sm(v[i]*Gp[i][j]*v[j] for i in range(3) for j in range(3))/2
    Xp=Rp-Pp;D=co['D'];f=co['f'];delta=co['delta0'];G=co['Gamma'];X=co['Xi']
    delta_log=fp/f-Dp/D;delta_p=delta*delta_log
    H=G**2/(3*D**2)-X/D
    Hp=2*G*gp/(3*D**2)-2*G**2*Dp/(3*D**3)-Xp/D+X*Dp/(D**2)
    C4p=delta**5*(5*delta_log*H+Hp)
    C2p=co['C2']*(3*delta_log+gp/G-Dp/D)
    return {'sign_moments':S,'sign_transport':srecords,'sign_partial_derivatives':Sd,'dual_rhs_root_terms':rterms,
      'dual_rhs':rhs,'dual_derivative_solve':solution,'b_prime':bp,'root_derivatives':records,
      'tail_derivative_bounds':tail,'derivatives':{'f':fp,'D':Dp,'delta0':delta_p,'Gamma':gp,
       'B':Bp,'G':Gp,'R':Rp,'P':Pp,'Xi':Xp,'C2':C2p,'C4':C4p},
      'C4_log_delta_contribution':delta**5*5*delta_log*H,'C4_shape_contribution':delta**5*Hp}
