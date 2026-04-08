from datetime import datetime
import random
import json
from typing import Dict, List, Any

class EventLog:
    def __init__(self):
        self.events=[]
        self.decisions=[]
        self.unexpected=[]
        self.timestamps=[]
    
    def add_event(self,month:int,severity:str,category:str,description:str,impact:Dict=None):
        evt={
            "month":month,
            "severity":severity,
            "category":category,
            "description":description,
            "impact":impact or {},
            "timestamp":datetime.now().isoformat()
        }
        self.events.append(evt)
    
    def add_decision(self,month:int,agent:str,action:str,options:List,chosen:str,reasoning:str):
        dec={
            "month":month,
            "agent":agent,
            "action":action,
            "options":options,
            "chosen":chosen,
            "reasoning":reasoning,
            "timestamp":datetime.now().isoformat()
        }
        self.decisions.append(dec)
    
    def add_unexpected(self,month:int,event_type:str,trigger:str,outcome:str,financial_impact:float):
        unexp={
            "month":month,
            "type":event_type,
            "trigger":trigger,
            "outcome":outcome,
            "impact":financial_impact,
            "timestamp":datetime.now().isoformat()
        }
        self.unexpected.append(unexp)
    
    def to_json(self):
        return {
            "events":self.events,
            "decisions":self.decisions,
            "unexpected_events":self.unexpected,
            "summary":{
                "total_events":len(self.events),
                "total_decisions":len(self.decisions),
                "total_unexpected":len(self.unexpected)
            }
        }


class UnexpectedEventGenerator:
    def __init__(self):
        self.events_catalog={
            "health":[
                {"name":"Sudden illness","prob":0.02,"impact":-5000},
                {"name":"Car accident","prob":0.01,"impact":-15000},
                {"name":"Job injury","prob":0.01,"impact":-10000},
                {"name":"Mental health crisis","prob":0.02,"impact":-8000},
            ],
            "financial":[
                {"name":"Market crash","prob":0.03,"impact":-0.15},
                {"name":"Unexpected bill","prob":0.05,"impact":-2000},
                {"name":"Freelance gig","prob":0.10,"impact":5000},
                {"name":"Tax refund","prob":0.04,"impact":3000},
                {"name":"Investment windfall","prob":0.02,"impact":25000},
            ],
            "social":[
                {"name":"Relationship conflict","prob":0.08,"cause":"stress","impact":"morale-10"},
                {"name":"Networking opportunity","prob":0.05,"cause":"event","impact":"network+50"},
                {"name":"Breakup","prob":0.03,"cause":"incompatibility","impact":"stress+30"},
                {"name":"Meet partner","prob":0.05,"cause":"social","impact":"committed"},
            ],
            "business":[
                {"name":"Startup acquires your interest","prob":0.02,"impact":"+equity"},
                {"name":"Startup pivot required","prob":0.03,"impact":"pmf-0.2"},
                {"name":"Key employee leaves","prob":0.04,"impact":"hc-1"},
                {"name":"Patent approved","prob":0.01,"impact":"+valuation"},
            ]
        }
    
    def generate(self,month:int,player_state):
        triggered=[]
        for category,events in self.events_catalog.items():
            for evt in events:
                if random.random()<evt["prob"]:
                    triggered.append({
                        "category":category,
                        "name":evt["name"],
                        "impact":evt.get("impact"),
                        "cause":evt.get("cause","random"),
                    })
        return triggered


class DecisionMaker:
    @staticmethod
    def make_business_decision(startup):
        options=["aggressive_hiring","conservative_growth","pivot","seek_funding","maintain"]
        choice=random.choice(options)
        
        if choice=="aggressive_hiring":
            startup.hc+=random.randint(5,15)
            startup.mor-=5
            startup.pay*=1.15
            impact={"headcount_change":"+10 avg","morale_impact":"-5","burn_increase":"15%"}
        elif choice=="conservative_growth":
            startup.gr*=0.8
            startup.mor+=3
            impact={"growth_reduction":"20%","morale_boost":"+3"}
        elif choice=="pivot":
            startup.pmf*=0.5
            startup.rev*=0.7
            impact={"pmf_reset":"50%","revenue_drop":"30%"}
        elif choice=="seek_funding":
            startup.fund("SEED",random.uniform(500e3,2e6))
            impact={"cash_increase":"✓","dilution":"+15% typical"}
        else:
            startup.mor+=2
            impact={"stability":"maintained"}
        
        return {"decision":choice,"impact":impact}
    
    @staticmethod
    def make_health_decision(health_profile):
        options=["increase_exercise","diet_change","stress_management","medical_checkup","ignore"]
        choice=random.choice(options)
        
        if choice=="increase_exercise":
            health_profile.exercise=min(10,health_profile.exercise+3)
            impact={"exercise_hours":"increase +3","health_score":"≈+5"}
        elif choice=="diet_change":
            impact={"diet_quality":"optimize","health_score":"≈+8"}
        elif choice=="stress_management":
            impact={"stress_reduction":"20-30%","morale":"boost +10"}
        elif choice=="medical_checkup":
            cost=-500
            impact={"cost":cost,"disease_early_detection":"probability +"}
        else:
            impact={"inaction":"health may decline"}
        
        return {"decision":choice,"impact":impact}
    
    @staticmethod
    def make_social_decision(partner):
        options=["commit_more","distance","propose","breakup","maintain"]
        choice=random.choice(options)
        
        if choice=="commit_more":
            partner.commit=min(100,partner.commit+20)
            impact={"commitment":"+20","relationship_quality":"+"}
        elif choice=="propose":
            if partner.commit>80:
                impact={"marriage":"YES","joint_assets":"combine","legal":"+positives"}
            else:
                impact={"rejection":"likely","commitment":"-10"}
        elif choice=="breakup":
            impact={"emotional_cost":"-20 morale","financial":"split","legal":"divorce process"}
        else:
            impact={"status":"quo"}
        
        return {"decision":choice,"impact":impact}
    
    @staticmethod
    def make_financial_decision(cash,investments,debt):
        options=["invest_more","pay_debt","save_cash","risky_trade","conservative"]
        choice=random.choice(options)
        
        if choice=="invest_more":
            invest_amt=cash*random.uniform(0.1,0.3)
            impact={"invested":invest_amt,"cash_reduction":invest_amt,"long_term":"growth+"}
        elif choice=="pay_debt":
            paydown=min(debt*0.2,cash*0.3)
            impact={"debt_reduction":paydown,"cash_outflow":paydown,"interest_savings":"future"}
        elif choice=="risky_trade":
            outcome=random.choice(["win","lose"])
            amt=cash*0.1
            if outcome=="win":
                impact={"gain":amt*random.uniform(1.5,3.0),"risk":"HIGH"}
            else:
                impact={"loss":amt,"risk":"HIGH"}
        else:
            impact={"stability":"maintained"}
        
        return {"decision":choice,"impact":impact}


class MonthlySimulator:
    def __init__(self,player_state,log:EventLog):
        self.state=player_state
        self.log=log
        self.unexpected_gen=UnexpectedEventGenerator()
    
    def simulate_month(self,month:int):
        month_log={
            "month":month,
            "events":[],
            "decisions":[],
            "unexpected":[],
            "state_before":{},
            "state_after":{}
        }
        
        ev_gen=UnexpectedEventGenerator()
        unexpected_events=ev_gen.generate(month,self.state)
        
        for unexp in unexpected_events:
            month_log["unexpected"].append(unexp)
            self.log.add_unexpected(month,unexp["category"],unexp["cause"],unexp["name"],unexp.get("impact",0))
        
        if hasattr(self.state,"startup"):
            biz_dec=DecisionMaker.make_business_decision(self.state.startup)
            month_log["decisions"].append({"domain":"business","decision":biz_dec["decision"],"impact":biz_dec["impact"]})
            self.log.add_decision(month,"entrepreneur","business_pivot",["aggressive","conservative","pivot","funding","maintain"],biz_dec["decision"],"Market conditions and runway considerations")
        
        if hasattr(self.state,"health"):
            health_dec=DecisionMaker.make_health_decision(self.state.health)
            month_log["decisions"].append({"domain":"health","decision":health_dec["decision"],"impact":health_dec["impact"]})
            self.log.add_decision(month,"player","health_action",["exercise","diet","stress","medical","ignore"],health_dec["decision"],"Health status monitoring")
        
        if self.state.partner:
            social_dec=DecisionMaker.make_social_decision(self.state.partner)
            month_log["decisions"].append({"domain":"social","decision":social_dec["decision"],"impact":social_dec["impact"]})
            self.log.add_decision(month,"player","relationship_action",["commit","distance","propose","breakup","maintain"],social_dec["decision"],"Relationship evaluation")
        
        financial_dec=DecisionMaker.make_financial_decision(
            getattr(self.state,"cash",0),
            getattr(self.state,"investments",0),
            getattr(self.state,"debt",0)
        )
        month_log["decisions"].append({"domain":"financial","decision":financial_dec["decision"],"impact":financial_dec["impact"]})
        self.log.add_decision(month,"player","asset_allocation",["invest","debt_paydown","save","trade","conservative"],financial_dec["decision"],"Portfolio optimization")
        
        self.log.add_event(month,"normal","monthly","Month completed with decisions and unexpected events")
        
        return month_log
