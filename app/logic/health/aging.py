import random
class HealthProfile:
    def __init__(self,age,bmi,smk,ex):
        self.age=age;self.bmi=bmi;self.smoking=smk;self.exercise=ex;self.score=50
    def calc_score(self):
        s=50+max(18-self.age/3,0)
        if self.bmi<18.5 or self.bmi>35:s-=10
        elif 25<=self.bmi:s-=5
        s-=25 if self.smoking else 5;s+=10 if self.exercise>5 else -15 if self.exercise<2 else 0
        self.score=max(0,min(100,s));return self.score
    def disease_onset(self):
        hd=(self.age/100*10)+random.uniform(0,5)+(5 if self.smoking else 0)+(5 if self.bmi>30 else 0)
        db=5 if self.age>50 else 0;db+=10 if self.bmi>30 else 0;ca=5 if self.smoking else 0
        return {"hd":hd,"db":db,"ca":ca}
def aging(age):
    energy=max(20,100-age/2);rec=1.5+age/30;return {"energy":energy,"recovery":rec}
def life_exp(health,smk,ex,stress):
    base=78+health/10-5-smk*10+ex*3-stress/20;return base+random.uniform(-3,3)
