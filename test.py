import pandas as pd
import matplotlib.pyplot as plt

# filenames
csv_files = ['1y.csv', '6m.csv', '1m.csv']

# prepare a list to store correlations
correlations = []

# read each CSV file, calculate correlation, and store it
for file in csv_files:
    df = pd.read_csv(file)
    correlation = df['Aggregated Exchanges'].corr(df['Price'])
    print(correlation)
    correlations.append(correlation)

# convert correlation to pandas Series for better visualization
correlations = pd.Series(correlations, index=['1 year', '6 months', '1 month'])

# plot correlation
plt.figure(figsize=(10,5))
correlations.plot(kind='bar', color='b')
plt.ylabel('Correlation')
plt.xlabel('Time Frame')
plt.title('Correlation of Aggregated Exchanges and Price over different time frames')
plt.grid(True)
plt.show()
