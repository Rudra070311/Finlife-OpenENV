import random
from datetime import datetime

class Partner:
    def __init__(self,pid,age,income,city):
        self.id=pid;self.age=age;self.income=income;self.city=city
        self.compat=50;self.commit=0;self.alive=True;self.meet_date=None
    def meet_prob(self,network=0,same_city=True):
        p=0.02+network*0.001;p*=1.2 if 25<self.age<40 else 1.0;p*=2.0 if same_city else 1.0
        return min(0.5,p)
    def monthly_dynamics(self):
        r=random.random();self.compat+=([-5,+10][r<0.03 and int(r<0.08)]);self.commit=min(100,self.commit+random.randint(2,5))

class Marriage:
    def __init__(self,ai_cash,spouse_income):
        self.joint=ai_cash+spouse_income*3;self.quality=70;self.kids=0
    def mfj_tax(self,ai_inc,sp_inc):
        j=ai_inc+sp_inc;t=0;prev=0
        for lim,r in [(10e3,0.1),(41e3,0.12),(89e3,0.22),(169e3,0.24)]:
            if j>lim:t+=(min(lim,j)-prev)*r;prev=lim
        return {"mfj":t,"mfs":0}
    def death_inherit(self):
        return self.joint+50000

def divorce(ai_inc,sp_inc,yrs,kids):
    assets=ai_inc*yrs*3/2;alimony=(sp_inc-ai_inc)*0.30*yrs/30/12 if sp_inc>ai_inc else 0
    cs=ai_inc*0.2*kids if ai_inc>sp_inc else 0;leg=random.choice([random.uniform(3e3,8e3),random.uniform(15e3,100e3)])
    return {"assets":assets,"alimony":alimony,"cs":cs,"legal":leg}

def networking(size,level):
    opp=1.0+(size*0.0005)+level*0.05;return {"size":size,"opp_mult":opp}
