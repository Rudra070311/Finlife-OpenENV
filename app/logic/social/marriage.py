from enum import Enum

class MarStatus(Enum):
    SINGLE="SINGLE";MARRIED="MARRIED";DIVORCED="DIVORCED";WIDOWED="WIDOWED"

class Marriage:
    def __init__(self,ai_cash,sp_income):
        self.joint=ai_cash+sp_income*3;self.quality=70;self.kids=0;self.status=MarStatus.MARRIED
    def taxes(self,ai_inc,sp_inc):
        j=ai_inc+sp_inc;t=0;prev=0
        for lim,r in [(10e3,0.1),(41e3,0.12),(89e3,0.22),(169e3,0.24)]:
            if j>lim:t+=(min(lim,j)-prev)*r;prev=lim
        return {"mfj":t}
    def inherit(self):return self.joint+50000
