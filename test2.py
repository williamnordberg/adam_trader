import pandas as pd
main_dataset = pd.read_csv('main_dataset.csv', dtype={146: str})

main_dataset = main_dataset.set_index('Date')
print(main_dataset.isnull().sum())
