import sys
sys.path.append("c:\\Users\\rudra\\OneDrive\\Documents\\VS_Code\\finlife-openenv")

from app.episode.runner import EpisodeRunner
from app.episode.output import OutputWriter


def main():
    print("\n" + "="*80)
    print("FINLIFE-OPENENV: EPISODE SIMULATION SYSTEM")
    print("="*80)
    
    num_months=12
    
    print(f"\nStarting {num_months}-month episode simulation...")
    
    runner=EpisodeRunner(num_months=num_months)
    report=runner.run()
    
    writer=OutputWriter()
    
    print("\n📁 Writing output files...")
    full_report_path=writer.write_full_report(report)
    narrative_path=writer.write_narrative(report)
    decision_tree_path=writer.write_decision_tree(report)
    summary_path=writer.write_summary(report)
    
    print("\n✨ All files written successfully!")
    print(f"\nOutput files:")
    print(f"  📊 Full Report: {full_report_path}")
    print(f"  📖 Narrative: {narrative_path}")
    print(f"  🌳 Decision Tree: {decision_tree_path}")
    print(f"  📋 Summary: {summary_path}")
    
    final_state=report.get("final_state",{})
    stats=report.get("statistics",{})
    
    print(f"\n🎯 EPISODE RESULTS:")
    print(f"   Final Net Worth: ${final_state.get('net_worth',0):,.0f}")
    print(f"   Net Worth Change: ${stats.get('net_worth_change',0):+,.0f}")
    print(f"   Total Decisions: {stats.get('total_decisions',0)}")
    print(f"   Unexpected Events: {stats.get('total_unexpected_events',0)}")
    print(f"   Startup Stage: {final_state.get('startup_stage','?')}")
    print(f"   Health Score: {final_state.get('health_score',0):.1f}/100")
    
    print("\n" + "="*80)
    print("✅ SIMULATION COMPLETE - All data exported to files")
    print("="*80 + "\n")


if __name__=="__main__":
    main()
