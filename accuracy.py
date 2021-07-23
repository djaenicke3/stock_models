import pandas as pd

df = pd.read_csv("Results.csv")

Real_val = [i for i in df["Real_values"]]
Pred_val = [i for i in df["predicted_value"]]

total = len(Real_val)

correct = 0
for i in range(1,len(Real_val)):
    if (Real_val[i]> Real_val[i-1]) and (Pred_val[i]>Pred_val[i-1]):
        correct+=1
    if (Real_val[i]< Real_val[i-1]) and (Pred_val[i]<Pred_val[i-1]):
        correct+=1

accuracy = (correct/total)*100
print(accuracy)

#print(df.head())