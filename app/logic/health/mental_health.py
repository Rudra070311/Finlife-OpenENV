import random
def stress_calc(baseline=20):
    stress=baseline;events={"job_loss":30,"death":40,"divorce":35,"promotion":"+15"}
    for e,v in events.items():
        if random.random()<0.05:stress+=v if isinstance(v,int) else int(v[1:])
    return max(0,min(100,stress))
def depression_risk(stress,untreated=False):
    base=0.02+stress/1000
    if untreated:base*=1.5
    return base
def treatment_cost(severity):
    if severity=="mild":return {"therapy":random.uniform(100,200),"meds":random.uniform(30,50)}
    elif severity=="moderate":return {"therapy":random.uniform(150,300),"meds":random.uniform(50,100)}
    else:return {"therapy":random.uniform(200,400),"meds":random.uniform(100,150)}
