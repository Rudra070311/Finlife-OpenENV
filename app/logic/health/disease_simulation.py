import random
class Disease:
    def __init__(self,name,onset_risk):self.name=name;self.risk=onset_risk;self.active=False
    def monthly_check(self):
        if random.random()<self.risk:self.active=True;return True
        return False
def hd_onset(age,smk,bmi):
    r=(age/100*10)+random.uniform(0,5)+(5 if smk else 0)+(5 if bmi>30 else 0);return r
def stroke_onset(age,bmi):return age/100*8+(5 if bmi>30 else 0)
def diabetes_onset(age,bmi):return (5 if age>50 else 0)+(10 if bmi>30 else 0)
def cancer_onset(smk):return 5 if smk else 1
