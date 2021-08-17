
from util import *
from tech_ind_model import predictions
df = pd.read_csv("Results.csv")

lst = ["AOS","AES","AAPL","GOOG", "MSFT", "AMZN","AOS","MMM","AMD","DOW"]
a ,b,c = predictions(lst)
a.to_csv("buy_hold.csv")
b.to_csv("rolling.csv")
c.to_csv("reinvest.csv")
