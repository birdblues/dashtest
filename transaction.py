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
        df = self.df
        df_etf_buy = df[df['거래상세유형']=='거래소주식[매수]'][['종목코드','거래금액','거래수량','종목명']]
        df_etf_sell = df[df['거래상세유형']=='거래소주식[매도]'][['종목코드','거래금액','거래수량','종목명']]
        df_cash_in = df[
            (df['거래상세유형'] == '기본부담금') | (df['거래상세유형'] == 'ETF분배금입금') | (df['거래상세유형'] == '정기대기이자입금')
            ][['종목코드','거래금액','거래수량','종목명']]
        df_cash_out = df[df['거래상세유형']=='현금[출금]'][['종목코드','거래금액','거래수량','종목명']]
        # print(df_cash_out)
        df_etf_sell['거래금액'] = df_etf_sell['거래금액'] * -1
        df_cash_out['거래금액'] = df_cash_out['거래금액'] * -1

        self.df_etf = pd.concat([df_etf_buy, df_etf_sell], axis=0)
        self.df_cash = pd.concat([df_cash_in, df_cash_out], axis=0)

        print(self.df_etf)
        print(self.df_cash)

        # 날짜별로 총합 구하기
        etf = self.df_etf['거래금액'].groupby(self.df_etf.index).sum()
        cash = self.df_cash['거래금액'].groupby(self.df_cash.index).sum()

        # Subtracting df2 from df1
        self.result_df = cash.sub(etf, fill_value=0).to_frame()

        self.result_df['예수금'] = self.result_df['거래금액'].cumsum()
        self.result_df = self.result_df.drop(['거래금액'], axis=1)

        self.종목코드표 = list(set(self.df.dropna()['종목코드']))
        print(self.종목코드표)

        self.dfprofit = pd.DataFrame()
        for code in self.종목코드표:
            # get_profit에서 리턴한 dataframe을 하나로 합치기
            self.dfprofit = pd.concat([self.dfprofit, self.get_profit(code, self.df_etf)], axis=1)

        self.dfprofit['total_etf'] = self.dfprofit.sum(axis=1)
        self.dfprofit = pd.concat([self.dfprofit, self.result_df], axis=1)
        # last 로 fillna
        self.dfprofit2 = self.dfprofit.fillna(method='ffill')
        self.dfprofit2 = self.dfprofit2.fillna(0)

        self.dfprofit2['총평가액'] = self.dfprofit2['예수금'] + self.dfprofit2['total_etf']

        self.dfprofit2.reset_index(inplace=True)
        self.dfprofit2['index'] = self.dfprofit2['index'].dt.date
        self.dfprofit2.set_index('index', inplace=True)
        print(self.dfprofit2)


    def get_profit(self, code: str, df):

        df_code = yf.Ticker(f'{code}.KS').history(period='1mo', interval='1d')[
            ['Open', 'High', 'Low', 'Close', 'Volume']]
        df_code = df_code['Close'].to_frame()

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
    
    def get_total(self):
        # print(self.dfprofit)
        return self.dfprofit
        
        
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
    # profit = data.get_profit_jason()
    # pprint(profit)
    # df_total = data.get_total()
    # pprint(df_total)
   
    


