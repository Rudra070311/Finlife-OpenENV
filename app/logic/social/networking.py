def networking(size,level):
    opp=1.0+(size*0.0005)+level*0.05;return {"size":size,"opp_mult":opp}
    rep=min(100,level*10+size*0.01);return {"rep":rep}
