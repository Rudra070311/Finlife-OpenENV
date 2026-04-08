import random

def q_sim(su,q):
    r=su.cf();return {"q":q,"rev":r.get("rev",0),"gp":r.get("gp",0),"ebitda":r.get("ebitda",0)}

def hire(su,n):
    su.hc+=n;su.pay*=1.1;su.mor=max(0,su.mor-2);return {"hc":su.hc,"pay":su.pay}

def price(su):
    m={"pen":{"mg":0.5,"gr":1.5},"comp":{"mg":0.65,"gr":1.2},"prem":{"mg":0.8,"gr":0.8},"val":{"mg":0.75,"gr":1.0}}
    ch=random.choice(list(m.keys()));return {"model":ch,"mg":m[ch]["mg"],"gr":m[ch]["gr"]}

def metrics(su):
    mrr=su.rev;arr=mrr*12;churn=0.05*(1-su.pmf);ltv=mrr/(churn+0.01) if churn>0 else mrr*12;cac=su.burn/su.hc if su.hc>0 else 0
    return {"mrr":mrr,"arr":arr,"churn":churn,"cac":cac,"ltv":ltv,"ratio":ltv/cac if cac>0 else 0}
