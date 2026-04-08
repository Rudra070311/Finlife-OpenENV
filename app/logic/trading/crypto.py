import random
class CryptoAsset:
    def __init__(self,sym,usd,ast="bitcoin"):
        self.sym=sym;self.inv=usd;self.price=50000 if ast=="bitcoin" else 3000;self.amt=usd/self.price
        self.vol=0.03 if ast in ["bitcoin","ethereum"] else 0.05;self.strat="HODL";self.fees=0
    def daily_move(self):
        dr=random.gauss(0,self.vol);self.price*=(1+dr);val=self.price*self.amt
        return {"price":self.price,"value":val,"return_pct":dr*100}
    def hold(self,mo=12):
        tr=1.0
        for d in range(mo*21):tr*=(1+random.gauss(0,self.vol))
        end=self.inv*tr;return {"end":end,"roi":(end-self.inv)/self.inv*100,"fees":0}
    def day_trade(self,mo=1,tw=5):
        trades=tw*4*mo;wins=int(trades*0.55);loss=trades-wins;gp=(wins*self.price*0.015)-(loss*self.price*0.01)
        fees=self.inv*0.002*trades;net=gp-fees;return {"trades":trades,"net":net,"roi":net/self.inv*100}

class ForexPos:
    def __init__(self,pair,usd,lev=1):
        self.pair=pair;self.cap=usd;self.pos_size=usd*lev;self.lev=lev;self.price=1.1;self.pnl=0
    def daily(self):
        dr=random.gauss(0,0.003);self.price*=(1+dr);self.pnl=(self.price-1.1)*self.pos_size;margin_level=(self.cap+self.pnl)/(self.pos_size/self.lev)*100
        return {"price":self.price,"pnl":self.pnl,"margin":margin_level,"margin_call":margin_level<20}
    def high_lev(self,days=30,lev=100):
        self.lev=lev;self.pos_size=self.cap*lev;pnl=0
        for d in range(days):mv=self.daily();pnl=mv["pnl"];ml=mv["margin_level"]
        if ml<5:return {"stopped":True,"loss":self.cap*0.95}
        return {"stopped":False,"pnl":pnl,"roi":pnl/self.cap*100,"margin":ml}

class Bond:
    def __init__(self,btype,face,coupon,yrs):
        self.type=btype;self.face=face;self.coupon_pct=coupon;self.yrs=yrs;self.income=0
        self.def_risk={"GOV":0.0001,"AAA":0.0015,"BBB":0.005,"JUNK":0.10}.get(btype,0.005)
    def annual_income(self):
        if random.random()<self.def_risk:return 0
        pmt=self.face*self.coupon_pct;self.income+=pmt;return pmt

class P2PLoan:
    def __init__(self,lid,princ,rate,grade):
        self.id=lid;self.princ=princ;self.rate=rate;self.grade=grade;self.mo=0
        self.def_risk={"A":0.01,"B":0.05,"C":0.10,"D":0.20}.get(grade,0.05);self.pay_mo=princ*rate/12
    def pay(self):
        if random.random()<self.def_risk/12:return {"def":True,"loss":self.princ*0.7}
        self.mo+=1;return {"def":False,"pay":self.pay_mo}

class Crowdfund:
    def __init__(self,cid,inv,eq):
        self.id=cid;self.inv=inv;self.eq=eq;self.val=inv/eq;self.yrs=0;self.status="ACTIVE"
    def journey(self,yrs=7):
        mult=1.0
        for y in range(yrs):
            if random.random()<0.3:mult*=random.uniform(1.5,3.0)
            else:mult*=random.uniform(0.95,1.05)
        r=random.random()
        if r<0.05:exit_type="UNICORN";exit_val=self.inv*random.uniform(50,200)
        elif r<0.25:exit_type="ACQ";exit_val=self.inv*random.uniform(2,5)
        else:exit_type="FAIL";exit_val=0
        return {"exit":exit_type,"val":exit_val,"roi":(exit_val-self.inv)/self.inv*100}
