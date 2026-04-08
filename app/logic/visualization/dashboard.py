from datetime import datetime
import random

class Dashboard:
    def __init__(self,state):
        self.state=state;self.refresh=datetime.now();self.alerts=[]
    def net_worth(self):
        assets=self.state.cash+self.state.invest+self.state.retire+self.state.re_equity
        liab=self.state.cc_debt+self.state.student_debt+self.state.mortgage
        return {"assets":assets,"liab":liab,"nw":assets-liab}
    def cash_flow(self):
        mi=self.state.salary/12;me=self.state.rent+self.state.insurance+self.state.food+200+100+self.state.taxes_mo
        surplus=mi-me;rate=surplus/mi*100 if mi>0 else 0
        if surplus<0:self.alerts.append({"level":"CRITICAL","msg":"Negative cash flow"})
        elif rate<10:self.alerts.append({"level":"WARNING","msg":"Low savings rate"})
        return {"mi":mi,"me":me,"surplus":surplus,"rate":rate}
    def alloc(self):
        tot=self.state.cash+self.state.invest+self.state.re_equity;pcts={}
        pcts["cash"]=self.state.cash/tot*100 if tot>0 else 0
        pcts["invest"]=self.state.invest/tot*100 if tot>0 else 0
        pcts["re"]=self.state.re_equity/tot*100 if tot>0 else 0
        return {"pcts":pcts,"total":tot}
    def summary(self):
        nw=self.net_worth();cf=self.cash_flow();al=self.alloc()
        return {"nw":nw["nw"],"cf":cf["surplus"],"alloc":al["pcts"],"alerts":self.alerts}

class Portfolio:
    def __init__(self,holdings):
        self.holdings=holdings
    def performance(self):
        tot_val=sum([h.get("val",0) for h in self.holdings])
        tot_cost=sum([h.get("cost",0) for h in self.holdings])
        ret=(tot_val-tot_cost)/tot_cost*100 if tot_cost>0 else 0
        return {"total":tot_val,"return_pct":ret}

class RetirementView:
    def __init__(self,age,life_exp,ret_save,salary):
        self.age=age;self.life_exp=life_exp;self.save=ret_save;self.sal=salary
    def project(self,ann_save=20e3,ret_age=67):
        yrs=max(0,ret_age-self.age);fut=self.save
        for y in range(yrs):fut=fut*1.07+ann_save
        withdraw=fut*0.04*12;exp=self.sal*0.7
        return {"future":fut,"annual_withdraw":withdraw,"sustainable":withdraw*12>=exp}
