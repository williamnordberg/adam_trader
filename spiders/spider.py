import pandas as pd
import scrapy


class BitcoinRichListSpider(scrapy.Spider):
    name = "bitcoin_rich_list2000_2"

    def __init__(self, *args, **kwargs):
        super(BitcoinRichListSpider, self).__init__(*args, **kwargs)
        self.base_url = "https://bitinfocharts.com/top-100-richest-bitcoin-addresses"
        self.start_urls = [f"{self.base_url}-{i}.html" for i in range(1, 21)]
        self.df = pd.DataFrame(columns=["address"])

    def parse(self, response):
        data = []
        for row in response.css("table tr"):
            data.append({
                "address": row.css("td:nth-of-type(2) a::text").get()
            })
        df2 = pd.DataFrame(data)
        self.df = self.df.append(df2, ignore_index=True)
        self.df.dropna(subset=["address"], inplace=True)
        self.df.to_csv("bitcoin_rich_list2000.csv", index=False)

    def get_df(self):
        print('df head in spider:', self.df.head())
        return self.df
