from typing import Optional,Dict,Any
import sys
sys.path.append('c:\\Users\\rudra\\OneDrive\\Documents\\VS_Code\\finlife-openenv')

from app.logic.business.startup import Startup,StartupStage
from app.logic.social.relationships import Partner
from app.logic.health.aging import HealthProfile
from app.logic.trading.crypto import CryptoAsset,ForexPos
from app.episode.events import EventLog,MonthlySimulator

class PlayerState:
    def __init__(self):
        self.month=0
        self.year=0
        self.age=25
        self.cash=100000
        self.debt=0
        self.investments=50000
        self.net_worth=self.cash+self.investments-self.debt
        
        self.startup=Startup("main","SAAS",0.80,100000,15000)
        self.partner=None
        self.health=HealthProfile(self.age,24,False,3)
        
        self.crypto_holdings={"BTC":0.5,"ETH":2.0}
        self.crypto_assets={
            "BTC":CryptoAsset("BTC",50000,"bitcoin"),
            "ETH":CryptoAsset("ETH",6000,"ethereum")
        }
        
        self.decisions_log=[]
        self.unexpected_events=[]
    
    def update_net_worth(self):
        crypto_value=sum(qty*self.crypto_assets[sym].price for sym,qty in self.crypto_holdings.items())
        startup_equity=self.startup.val*self.startup.fe if hasattr(self.startup,"val") else 0
        self.net_worth=self.cash+self.investments+crypto_value+startup_equity-self.debt
    
    def snapshot(self)->Dict[str,Any]:
        return {
            "month":self.month,
            "year":self.year,
            "age":self.age,
            "cash":self.cash,
            "debt":self.debt,
            "investments":self.investments,
            "net_worth":self.net_worth,
            "startup_stage":str(self.startup.stage) if hasattr(self.startup,"stage") else "IDEA",
            "startup_valuation":getattr(self.startup,"val",0),
            "startup_pmf":getattr(self.startup,"pmf",0),
            "health_score":self.health.score if hasattr(self.health,"score") else 0,
            "partner_committed":self.partner.commit if self.partner else None,
        }


class EpisodeRunner:
    def __init__(self,num_months:int=12):
        self.num_months=num_months
        self.state=PlayerState()
        self.log=EventLog()
        self.simulator=MonthlySimulator(self.state,self.log)
        self.monthly_snapshots=[]
    
    def run(self)->Dict[str,Any]:
        print(f"\n🎬 EPISODE RUNNER STARTED - {self.num_months} MONTHS")
        print("="*70)
        
        for month in range(1,self.num_months+1):
            self.state.month=month
            self.state.year=month//12+2026
            
            print(f"\n📅 MONTH {month}/{self.num_months} (Year {self.state.year})")
            print("-"*70)
            
            month_results=self.simulator.simulate_month(month)
            
            print(f"💼 Business: {self.state.startup.stage} | PMF: {getattr(self.state.startup,'pmf',0):.1%}")
            if month_results["decisions"]:
                for dec in month_results["decisions"]:
                    if dec["domain"]=="business":
                        print(f"   Decision: {dec['decision'].upper()}")
                        for k,v in dec["impact"].items():
                            print(f"      → {k}: {v}")
            
            if month_results["unexpected"]:
                print(f"\n⚠️  UNEXPECTED EVENTS ({len(month_results['unexpected'])}):")
                for unexp in month_results["unexpected"]:
                    print(f"   [{unexp['category'].upper()}] {unexp['name']}")
                    print(f"      Cause: {unexp['cause']} | Impact: {unexp['impact']}")
            
            print(f"\n❤️  Health: {self.state.health.score if hasattr(self.state.health,'score') else 0:.1f}/100")
            
            if self.state.partner:
                print(f"💑 Relationship: {self.state.partner.name} (Commitment: {self.state.partner.commit:.0f}%)")
            
            print(f"\n💰 Financial State:")
            print(f"   Cash: ${self.state.cash:,.0f}")
            print(f"   Investments: ${self.state.investments:,.0f}")
            print(f"   Debt: ${self.state.debt:,.0f}")
            self.state.update_net_worth()
            print(f"   Net Worth: ${self.state.net_worth:,.0f}")
            
            self.monthly_snapshots.append(self.state.snapshot())
        
        print("\n" + "="*70)
        print("🏁 EPISODE COMPLETE")
        print("="*70)
        
        return self.compile_report()
    
    def compile_report(self)->Dict[str,Any]:
        return {
            "episode_metadata":{
                "duration_months":self.num_months,
                "start_year":2026,
                "end_year":2026+(self.num_months//12),
                "player_start_age":25,
                "player_end_age":25+(self.num_months//12)
            },
            "final_state":self.state.snapshot(),
            "monthly_snapshots":self.monthly_snapshots,
            "event_log":self.log.to_json(),
            "statistics":{
                "total_unexpected_events":len(self.log.unexpected),
                "total_decisions":len(self.log.decisions),
                "total_events":len(self.log.events),
                "net_worth_change":self.monthly_snapshots[-1]["net_worth"]-100000 if self.monthly_snapshots else 0,
                "decisions_by_domain":self._group_decisions_by_domain()
            }
        }
    
    def _group_decisions_by_domain(self)->Dict[str,int]:
        domains={}
        for dec in self.log.decisions:
            agent=dec["agent"]
            domains[agent]=domains.get(agent,0)+1
        return domains
