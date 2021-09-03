
from util import *
from tech_ind_model import predictions
#df = pd.read_csv("Results.csv")

lst = ["SPY"]
a ,b,c, accuracy = predictions(lst)
a.to_csv("buy_hold.csv")
b.to_csv("rolling.csv")
c.to_csv("reinvest.csv")

print(accuracy)
#print(Bull_twok_csv(real,pred))