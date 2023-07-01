import pandas as pd


def remove_duplicates(csv_file):
    # Read the csv file
    df = pd.read_csv(csv_file, header=None, skipinitialspace=True)

    # Remove duplicates
    df.drop_duplicates(inplace=True)

    # Write the data back to csv
    df.to_csv(csv_file, index=False, header=False)


def check_common_addresses(csv_file1, csv_file2):
    # Read the csv files
    df1 = pd.read_csv(csv_file1, header=None, skipinitialspace=True)
    df2 = pd.read_csv(csv_file2, header=None, skipinitialspace=True)

    # Find common addresses
    common_addresses = pd.merge(df1, df2, how='inner')

    if not common_addresses.empty:
        print("Common addresses found:")
        print(common_addresses)
    else:
        print("No common addresses found.")


def remove_trailing_spaces(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    with open(filename, 'w') as file:
        for line in lines:
            file.write(line.rstrip() + '\n')


remove_trailing_spaces('data/exchange_addresses.csv')


# check_common_addresses('data/exchange_adresses.csv', 'data/bitcoin_rich_list2000.csv')

# remove_duplicates('data/exchange_addresses.csv')
