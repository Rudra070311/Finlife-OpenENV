import random
def salary_neg(curr_sal,market_rate,perf):
    prob={"excellent":0.7,"good":0.55,"fair":0.3}.get(perf,0.3)
    raise_pct=0.10*{"excellent":1.0,"good":0.75,"fair":0.5}.get(perf,0.5)
    if random.random()<prob:return {"success":True,"new_sal":curr_sal*(1+raise_pct)}
    return {"success":False,"sal":curr_sal}
def mortgage_refi(rate,bal,yrs):
    new_rate=rate-0.02
    if new_rate>=rate:return {"refi":False}
    cost=random.uniform(1000,5000);monthly_save=bal/yrs/12*0.02;breakeven=cost/monthly_save if monthly_save>0 else 999
    return {"refi":breakeven<60,"cost":cost,"save":monthly_save,"breakeven_mo":breakeven}
