import pandas as pd
from util import *
df = pd.read_csv("Results.csv")
# data = data.drop('Date', axis=1)
# data = data.drop('Volume', axis=1)
# data = data.drop(0, axis=0)
#
# train_split =len(data.values) -int(len(data.values)/10)
# print(data.values[:675])

Real_val = [i for i in df["Real_values"]]
Pred_val = [i for i in df["predicted_value"]]

total = len(Real_val)
# print(compute_earnings(Real_val,Pred_val))
correct = 1
for i in range(1,len(Real_val)):
    if (Real_val[i]> Real_val[i-1]) and (Pred_val[i]>Pred_val[i-1]):
        correct+=1
    if (Real_val[i]< Real_val[i-1]) and (Pred_val[i]<Pred_val[i-1]):
        correct+=1
print(correct)
accuracy = (correct/total)*100
print(accuracy)
print(Bull_twok(Real_val,Pred_val))
print(buy_hold(Real_val, Pred_val))
#print(df.head())

(Bull_twok_csv(Real_val, Pred_val)).to_csv("Danresults.csv")