import pandas as pd
import yfinance as yf
import numpy as np
import json

class TransactionData:
    def __init__(self, csvFile='거래내역.csv'):

        # Set display format for floating point numbers
        pd.set_option('display.float_format', '{:.2f}'.format)

        # Read the CSV file into a DataFrame, ensuring the stock codes are read as strings
        self.df = pd.read_csv(csvFile, dtype={'종목코드': str})

        # Convert the '주문일자' column to datetime format with timezone
        self.df['주문일자'] = pd.to_datetime(self.df['주문일자']).dt.tz_localize('Asia/Seoul')
        self.df.set_index('주문일자', inplace=True)

        # Display the DataFrame
        # print(self.df)
        
        self.종목코드표 = list(set(self.df.dropna()['종목코드']))
        print(self.종목코드표)

        self.dfprofit = pd.DataFrame()
        for code in self.종목코드표:
            # get_profit에서 리턴한 dataframe을 하나로 합치기
            self.dfprofit = pd.concat([self.dfprofit, self.get_profit(code, self.df)], axis=1)

        self.dfprofit.reset_index(inplace=True)
        self.dfprofit['Date'] = self.dfprofit['Date'].dt.date
        self.dfprofit.set_index('Date', inplace=True)
        # print(self.dfprofit)


    def get_profit(self, code: str, df):

        df_code = yf.Ticker(f'{code}.KS').history(period='1mo', interval='1d')[
            ['Open', 'High', 'Low', 'Close', 'Volume']]
        df_code = df_code['Close'].to_frame()

        # print(df_code)

        df['거래금액'] = df.apply(
            lambda row: row['거래금액'] if row['거래상세유형'] == '거래소주식[매수]' else -row['거래금액'],
            axis=1)

        df_code['거래금액'] = df.loc[df['종목코드'] == code, '거래금액']
        df_code['거래수량'] = df.loc[df['종목코드'] == code, '거래수량']

        # NaN부분은 0으로 시작
        df_code['거래금액'] = df_code['거래금액'].fillna(0)
        df_code['거래수량'] = df_code['거래수량'].fillna(0)

        # 시간별 누적금액을 추가
        df_code['누적금액'] = df_code['거래금액'].cumsum()
        df_code['누적수량'] = df_code['거래수량'].cumsum()
        # 단가는
        df_code['단가'] = df_code['누적금액'] / df_code['누적수량']
        df_code['단가'] = df_code['단가'].fillna(0)
        df_code['수익률'] = (df_code['Close'] - df_code['단가']) / df_code['단가'] * 100

        # inf를 0으로 바꿈
        df_code = df_code.replace([np.inf, -np.inf], 0)
        df_code[code] = df_code['수익률'] * df_code['누적금액'] / 100 + df_code['누적금액']

        return df_code[code].to_frame()
        
    def get_profit_jason(self):
        list_profit = []
        for code in self.종목코드표:
            df = self.get_profit(code, self.df)
            df['time'] = df.index.strftime('%Y-%m-%d')
            df['value'] = df[code].astype('float')
            list_profit.append(json.loads(df[['time', 'value']].to_json(orient='records')))
        return list_profit
    
    def get_code_list(self):
        return self.종목코드표
    
    def get_code_name(self):
        list_name = []
        for code in self.종목코드표:
            list_name.append(
                self.df.loc[
                    self.df['종목코드'] == code, '종목명'].iloc[0])
        return list_name

from pprint import pprint
if __name__ == '__main__':
    data = TransactionData()
    profit = data.get_profit_jason()
    pprint(profit)
    print(len(profit))
    list_code = data.get_code_list()
    print(list_code)
    


