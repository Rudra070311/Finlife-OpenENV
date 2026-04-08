class Equity:
    def __init__(self,sid,amt,pct):self.sid=sid;self.amt=amt;self.pct=pct
    def value(self,sv):return sv*self.pct
    def dilute(self,dil_pct):self.pct*=(1-dil_pct)
