% Independent GNU Octave reference: QP / LP / ODE / game matrices.
% Usage: octave --quiet math/reference_octave.m <output.json>
args=argv(); if isempty(args), destination='evidence/math_octave_reference.json'; else destination=args{1}; endif
H=diag([2,4]); q=[-6;8]; lb=[0;-1]; ub=[2;3];
[x,obj,info,lambda]=qp([0;0],H,q,[],[],lb,ub);
grad=H*x+q;
kkt=max([0; max(0,grad(1)); max(0,-grad(2))]);
% Independent linear optimizer adds a second objective family.
[cx,cf,cstatus,cextra]=glpk([1;2],[1,1],3,[0;0],[10;10],'L','CC',1);
opts=odeset('RelTol',1e-11,'AbsTol',1e-13);
[tt,yy]=ode45(@(t,y) -.7*y,[0,4],3,opts);
result=struct('solver','GNU Octave','version',version(),'qp',struct('status',info.info,'primal',x','objective',obj,'gradient',grad','kkt_inf',kkt),'lp',struct('primal',cx','objective',cf,'errnum',cstatus,'status',cextra.status),'ode',struct('equation','dy/dt=-0.7*y','final',yy(end),'analytic',3*exp(-2.8),'residual',abs(yy(end)-3*exp(-2.8)),'samples',length(tt)));
f=fopen(destination,'w'); fprintf(f,'%s\n',jsonencode(result)); fclose(f);
