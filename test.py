import pandas as pd

df = pd.read_csv('1y.csv', index_col=False)

correlation_all = df['Inflow'].corr(df['Price'])

df1 = pd.read_csv('6m.csv', index_col=False)

correlation_1y = df1['Inflow'].corr(df['Price'])

df2 = pd.read_csv('1m.csv', index_col=False)

correlation_6m = df2['Inflow'].corr(df['Price'])


print('correlation_all', correlation_all)
print('correlation_1y', correlation_1y)
print('correlation_6m', correlation_6m)

