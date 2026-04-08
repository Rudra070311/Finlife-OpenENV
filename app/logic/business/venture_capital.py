import random

class VC:
    def __init__(self,name,aum):self.name=name;self.aum=aum;self.port=[]
    def invest(self,su,amt):su.fund("SEED",amt);self.port.append(su);return {"invested":amt}
    def liquidate(self,su,val):
        for s in self.port:
            if s.id==su.id:self.port.remove(s);return {"liquidated":True,"val":val}
        return {"liquidated":False}
