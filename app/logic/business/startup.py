from datetime import datetime
from enum import Enum
import random

class StartupStage(Enum):
    IDEA="IDEA";SEED="SEED";SERIES_A="SERIES_A";SERIES_B="SERIES_B";SERIES_C="SERIES_C";IPO="IPO";ACQUIRED="ACQUIRED";BANKRUPT="BANKRUPT"

class Startup:
    def __init__(self,id,sector,fe,cap,burn):
        self.id=id;self.sec=sector;self.fe=fe;self.cash=cap;self.burn=burn;self.stage=StartupStage.IDEA;self.mo=0;self.val=1e6;self.ct={"f":fe,"i":{},"e":{}}
        self.rev=100 if sector=="SAAS" else 50;self.pmf=0.1;self.gr=0.05;self.hc=1;self.pay=burn*0.6;self.mor=50;self.atn=0.1;self.hist=[]
    def cf(self):
        if self.stage in [StartupStage.BANKRUPT,StartupStage.ACQUIRED,StartupStage.IPO]:return {}
        if self.pmf>0.5:self.rev*=(1+self.gr);self.gr*=1.02;self.mor+=1
        else:self.rev*=0.98;self.mor-=1
        cogs=self.rev*0.25;gp=self.rev-cogs;opex=self.pay+gp*0.75;ebitda=gp-opex;self.cash-=opex
        if self.cash<0:self.stage=StartupStage.BANKRUPT
        self.hist.append((self.rev,opex));self.runway=self.cash/opex if opex>0 else 999
        return {"rev":self.rev,"cogs":cogs,"gp":gp,"opex":opex,"ebitda":ebitda,"cash":self.cash,"runway":self.runway}
    def pmf_chk(self):
        b=0.2+(self.mo/60)*0.15
        if len(self.hist)>3 and sum([h[0] for h in self.hist[-3:]])>sum([h[0] for h in self.hist[-6:-3]]):b+=0.25
        if random.random()<b:self.pmf=min(1.0,self.pmf+random.uniform(0.15,0.35));self.mor+=20;return True
        self.pmf=max(0,self.pmf-0.02);return False
    def fund(self,s,amt,val=None):
        if self.stage==StartupStage.BANKRUPT:return {"ok":False}
        pm=val or self.val*{"SEED":2,"SERIES_A":3.5,"SERIES_B":5,"SERIES_C":8}.get(s,2)
        dil=amt/pm;self.fe*=(1-dil);self.cash+=amt;self.val=pm;self.stage=StartupStage[s] if s in ["SEED","SERIES_A","SERIES_B","SERIES_C"] else self.stage
        self.burn*=1.3;self.hc+=5;self.pay*=1.25;self.mor+=25;return {"ok":True,"s":s,"pm":pm,"fe":self.fe}
    def acq(self,buyer,val):
        if self.stage in [StartupStage.BANKRUPT,StartupStage.ACQUIRED]:return {"ok":False}
        fp=val*self.fe;self.stage=StartupStage.ACQUIRED;return {"ok":True,"buyer":buyer,"val":val,"fp":fp}
    def ipo(self):
        if sum(self.hist[-12:] if len(self.hist)>=12 else [])>100e6 and self.val>1e9:
            self.stage=StartupStage.IPO;return {"ok":True,"val":self.val}
        return {"ok":False}
    def upd(self):
        self.mo+=1;self.cf();random.random()<0.1 and self.pmf_chk()
        if random.random()<self.atn:self.hc=max(1,self.hc-1);self.mor-=5
        if self.mor>70:self.gr*=1.05
        elif self.mor<30:self.gr*=0.9
        self.mor=max(0,min(100,self.mor-2))
