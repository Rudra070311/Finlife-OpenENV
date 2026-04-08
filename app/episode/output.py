import json
from pathlib import Path
from datetime import datetime
from typing import Dict,Any

class OutputWriter:
    def __init__(self,output_dir:str="c:\\Users\\rudra\\OneDrive\\Documents\\VS_Code\\finlife-openenv\\episode_outputs"):
        self.output_dir=Path(output_dir)
        self.output_dir.mkdir(parents=True,exist_ok=True)
        self.timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def write_full_report(self,report:Dict[str,Any])->str:
        filename=self.output_dir/f"episode_{self.timestamp}_full.json"
        with open(filename,"w") as f:
            json.dump(report,f,indent=2,default=str)
        print(f"\n✅ Full report written to: {filename}")
        return str(filename)
    
    def write_narrative(self,report:Dict[str,Any])->str:
        filename=self.output_dir/f"episode_{self.timestamp}_narrative.txt"
        
        with open(filename,"w",encoding="utf-8") as f:
            f.write("="*80+"\n")
            f.write("FINLIFE-OPENENV: EPISODE SIMULATION REPORT\n")
            f.write("="*80+"\n\n")
            
            metadata=report.get("episode_metadata",{})
            f.write(f"📊 EPISODE METADATA\n")
            f.write("-"*80+"\n")
            f.write(f"Duration: {metadata.get('duration_months',0)} months\n")
            f.write(f"Years: {metadata.get('start_year',0)} - {metadata.get('end_year',0)}\n")
            f.write(f"Player Age: {metadata.get('player_start_age',0)} → {metadata.get('player_end_age',0)}\n\n")
            
            final_state=report.get("final_state",{})
            f.write(f"💰 FINAL FINANCIAL STATE\n")
            f.write("-"*80+"\n")
            f.write(f"Cash: ${final_state.get('cash',0):,.2f}\n")
            f.write(f"Investments: ${final_state.get('investments',0):,.2f}\n")
            f.write(f"Debt: ${final_state.get('debt',0):,.2f}\n")
            f.write(f"Net Worth: ${final_state.get('net_worth',0):,.2f}\n\n")
            
            stats=report.get("statistics",{})
            net_worth_change=stats.get('net_worth_change',0)
            f.write(f"📈 GROWTH: ${net_worth_change:+,.2f}\n\n")
            
            f.write(f"🏢 BUSINESS STATUS\n")
            f.write("-"*80+"\n")
            f.write(f"Stage: {final_state.get('startup_stage','IDEA')}\n")
            f.write(f"Valuation: ${final_state.get('startup_valuation',0):,.2f}\n")
            f.write(f"PMF Score: {final_state.get('startup_pmf',0):.1%}\n\n")
            
            f.write(f"🏥 HEALTH STATUS\n")
            f.write("-"*80+"\n")
            f.write(f"Health Score: {final_state.get('health_score',0):.1f}/100\n\n")
            
            event_log=report.get("event_log",{})
            f.write(f"📋 EVENT SUMMARY\n")
            f.write("-"*80+"\n")
            f.write(f"Total Events: {event_log.get('summary',{}).get('total_events',0)}\n")
            f.write(f"Total Decisions: {event_log.get('summary',{}).get('total_decisions',0)}\n")
            f.write(f"Unexpected Events: {event_log.get('summary',{}).get('total_unexpected',0)}\n\n")
            
            f.write(f"🎯 DETAILED DECISION LOG\n")
            f.write("="*80+"\n")
            for i,dec in enumerate(event_log.get("decisions",[]),1):
                f.write(f"\n[{i}] Month {dec.get('month',0)} - {dec.get('agent','UNKNOWN').upper()}\n")
                f.write(f"Action: {dec.get('action','N/A')}\n")
                f.write(f"Options: {', '.join(dec.get('options',[]))}\n")
                f.write(f"Chosen: {dec.get('chosen','UNKNOWN').upper()}\n")
                f.write(f"Reasoning: {dec.get('reasoning','N/A')}\n")
            
            f.write(f"\n\n⚠️  UNEXPECTED EVENTS LOG\n")
            f.write("="*80+"\n")
            for i,unexp in enumerate(event_log.get("unexpected_events",[]),1):
                f.write(f"\n[{i}] Month {unexp.get('month',0)} - {unexp.get('type','UNKNOWN').upper()}\n")
                f.write(f"Event: {unexp.get('outcome','Unknown event')}\n")
                f.write(f"Trigger: {unexp.get('trigger','Unknown')}\n")
                impact=unexp.get('impact',0)
                if isinstance(impact,str):
                    f.write(f"Impact: {impact}\n")
                else:
                    f.write(f"Financial Impact: ${impact:+,.2f}\n")
            
            f.write(f"\n\n📅 MONTHLY SNAPSHOTS\n")
            f.write("="*80+"\n")
            for mon in report.get("monthly_snapshots",[]):
                f.write(f"\nMonth {mon.get('month',0)} | Age {mon.get('age',0)}\n")
                f.write(f"  Net Worth: ${mon.get('net_worth',0):,.2f}\n")
                f.write(f"  Startup: {mon.get('startup_stage','?')} (PMF: {mon.get('startup_pmf',0):.1%})\n")
                f.write(f"  Health: {mon.get('health_score',0):.1f}/100\n")
            
            f.write(f"\n\n" + "="*80+"\n")
            f.write("END OF REPORT\n")
            f.write("="*80+"\n")
        
        print(f"\n✅ Narrative report written to: {filename}")
        return str(filename)
    
    def write_decision_tree(self,report:Dict[str,Any])->str:
        filename=self.output_dir/f"episode_{self.timestamp}_decisions.txt"
        
        with open(filename,"w",encoding="utf-8") as f:
            f.write("DECISION TREE & CAUSALITY ANALYSIS\n")
            f.write("="*80+"\n\n")
            
            event_log=report.get("event_log",{})
            decisions=event_log.get("decisions",[])
            unexpected=event_log.get("unexpected_events",[])
            
            f.write("COMBINED CHRONOLOGICAL TIMELINE\n")
            f.write("-"*80+"\n\n")
            
            timeline=[]
            for dec in decisions:
                timeline.append(("decision",dec))
            for unexp in unexpected:
                timeline.append(("unexpected",unexp))
            
            timeline.sort(key=lambda x: x[1].get("month",0))
            
            for evt_type,evt in timeline:
                if evt_type=="decision":
                    f.write(f"[M{evt.get('month',0)}] DECISION BY {evt.get('agent','?').upper()}\n")
                    f.write(f"  Action Type: {evt.get('action','?')}\n")
                    f.write(f"  Possible Choices: {', '.join(evt.get('options',[]))}\n")
                    f.write(f"  → CHOSE: {evt.get('chosen','?').upper()}\n")
                    f.write(f"  Reasoning: {evt.get('reasoning','N/A')}\n\n")
                else:
                    f.write(f"[M{evt.get('month',0)}] ⚠️  UNEXPECTED EVENT\n")
                    f.write(f"  Type: {evt.get('type','?')}\n")
                    f.write(f"  Triggered By: {evt.get('trigger','?')}\n")
                    f.write(f"  Outcome: {evt.get('outcome','?')}\n")
                    impact=evt.get('impact',0)
                    if isinstance(impact,str):
                        f.write(f"  Impact: {impact}\n\n")
                    else:
                        f.write(f"  Financial Impact: ${impact:+,.2f}\n\n")
        
        print(f"\n✅ Decision tree written to: {filename}")
        return str(filename)
    
    def write_summary(self,report:Dict[str,Any])->str:
        filename=self.output_dir/f"episode_{self.timestamp}_summary.txt"
        
        with open(filename,"w",encoding="utf-8") as f:
            f.write("EPISODE SUMMARY\n")
            f.write("="*80+"\n\n")
            
            final=report.get("final_state",{})
            stats=report.get("statistics",{})
            
            f.write(f"Final Net Worth: ${final.get('net_worth',0):,.2f}\n")
            f.write(f"Change: ${stats.get('net_worth_change',0):+,.2f}\n")
            f.write(f"Startup Stage: {final.get('startup_stage','?')}\n")
            f.write(f"Startup PMF: {final.get('startup_pmf',0):.1%}\n")
            f.write(f"Health Score: {final.get('health_score',0):.1f}/100\n\n")
            
            f.write(f"Decision Statistics:\n")
            for agent,count in stats.get("decisions_by_domain",{}).items():
                f.write(f"  {agent}: {count} decisions\n")
            
            f.write(f"\nUnexpected Events: {stats.get('total_unexpected_events',0)}\n")
        
        print(f"\n✅ Summary written to: {filename}")
        return str(filename)
