def wellness_score(age,bmi,ex,stress,sleep):
    s=50+max(18-age/3,0)
    if bmi<18.5 or bmi>35:s-=10
    elif 25<=bmi:s-=5
    s+=10 if ex>5 else -15 if ex<2 else 0
    s+=5 if 7<=sleep<=9 else -10 if sleep<5 else 0
    s-=15 if stress>60 else -5 if stress>30 else 0
    return max(0,min(100,s))
