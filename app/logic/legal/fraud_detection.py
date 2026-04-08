import random
def fraud_types():
    return {"identity_theft":{"cost":50,"score_hit":20},"home":{"cost":random.uniform(5e3,20e3)},"invest":{"loss":random.uniform(10e3,500e3)}}
def detect_fraud(score):
    risk=1.0-score/100;return random.random()<risk/10
