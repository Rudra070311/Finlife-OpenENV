def estate_plan(nw):
    est_cost=nw*0.05;will_cost=random.uniform(200,1e3);trust=random.uniform(1500,3000);poa=random.uniform(100,500)
    return {"intestate":est_cost,"will":will_cost,"trust":trust,"poa":poa}
