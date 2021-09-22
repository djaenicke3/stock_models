
from util import *
from tech_ind_model import predictions
#df = pd.read_csv("Results.csv")

lst = ["SPY"]
a ,b,c,d,acc = predictions(lst)
a.to_csv("buy_hold.csv")
b.to_csv("rolling.csv")
c.to_csv("reinvest.csv")
d.to_csv("new_strategy.csv")
print(acc)


