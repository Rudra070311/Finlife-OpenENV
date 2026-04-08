import random
def proc_div(ai_inc,sp_inc,yrs,kids):
    assets=ai_inc*yrs*3/2;alimony=(sp_inc-ai_inc)*0.30*yrs/30/12 if sp_inc>ai_inc else 0
    cs=ai_inc*0.2*kids if ai_inc>sp_inc else 0;leg=random.choice([random.uniform(3e3,8e3),random.uniform(15e3,100e3)])
    return {"assets":assets,"alimony":alimony,"cs":cs,"legal":leg}
