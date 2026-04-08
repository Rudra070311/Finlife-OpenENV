import random
from enum import Enum
class CaseStage(Enum):
    INIT="INIT";DISC="DISCOVERY";MED="MEDIATION";TRIAL="TRIAL";SETTLED="SETTLED";WON="WON";LOST="LOST"
class Case:
    def __init__(self,id,ctype,is_pl,party,amt):
        self.id=id;self.type=ctype;self.pl=is_pl;self.party=party;self.amt=amt
        self.stage=CaseStage.INIT;self.atty=False;self.cost=0;self.strength=random.uniform(10,90)
    def hire_atty(self):
        self.atty=True;self.cost+=random.uniform(2000,10000);return {"atty":True,"rate":random.uniform(200,500)}
    def discovery(self,mo=9):
        disc_cost=random.uniform(10000,40000);self.cost+=disc_cost;self.stage=CaseStage.DISC;return {"cost":disc_cost}
    def mediate(self):
        if random.random()<0.65:
            settle=self.amt*self.strength/100*random.uniform(0.7,0.9);self.stage=CaseStage.SETTLED
            return {"settled":True,"amt":settle,"cost":self.cost}
        else:return {"settled":False}
    def trial(self):
        tcost=random.uniform(10e3,500e3);self.cost+=tcost;outcome="WON" if random.random()<self.strength/100 else "LOST"
        award=self.amt*(1+random.uniform(-0.2,0.1)) if outcome=="WON" else 0;self.stage=CaseStage[outcome];net=award-self.cost
        return {"outcome":outcome,"award":award,"trial_cost":tcost,"net":net}
