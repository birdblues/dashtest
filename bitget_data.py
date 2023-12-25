import ccxt
import os
import time
import threading
import pandas as pd
from pprint import pprint
import json
import numpy as np
from prophet import Prophet

class BitgetData:
    def __init__(self, symbol='BTC/USDT'):
        
        self.symbol = symbol
        self.exchange = ccxt.bitget({
            # 'apiKey': api_key,
            # 'secret': api_secret,
            # 'password': api_passphrase,
            'options': {
                'defaultType': 'future',
            },
            'verbose': False,
        })

        self.csvfile = f'bitget_{self.symbol.replace("/","")}.csv'
        if not os.path.exists(self.csvfile):
            # 시간 설정
            end_time = self.exchange.milliseconds()
            start_time = end_time - 30 * 24 * 60 * 60 * 1000

            # 데이터를 담을 리스트 초기화
            all_ohlcv = []

            # 데이터를 가져오기
            while start_time < end_time:
                #밀리세컨드를 datetime으로 변경
                print(pd.to_datetime(start_time, unit='ms'))
                print(pd.to_datetime(end_time, unit='ms'))
                ohlcv = self.exchange.fetch_ohlcv(self.symbol, '1m', since=start_time, limit=1000)
                df = pd.DataFrame(ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
                df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
                if not ohlcv:
                    break
                start_time = ohlcv[-1][0] + 1
                all_ohlcv.extend(ohlcv)
                time.sleep(1)

                df = pd.DataFrame(all_ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
                df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')

                df.set_index('datetime', inplace=True)
                df.to_csv(self.csvfile)

        self.df = pd.read_csv(self.csvfile, index_col=0)
        self.df.index = pd.to_datetime(self.df.index)
        self.get_ohlcv()
        self.df.to_csv(self.csvfile)

        self.stop_thread = False
        self.thread = threading.Thread(target=self.run_thread)
        try:
            self.thread.start()
        except Exception as e:
            print(f"An error occurred: {e}")
            self.stop_thread = True

    def run_thread(self):
        while not self.stop_thread:
            print("Thread 1")
            self.get_ohlcv()
            time.sleep(1)

    def __del__(self):
        self.stop_thread = True
        if self.thread.is_alive():
            self.thread.join()

    def get_ohlcv(self):
        # 시간 설정
        end_time = self.exchange.milliseconds()
        #df의 마지막 인덱스값을 milliseconds로 변경
        start_time = self.df.index[-1].value // 1000000
        # 데이터를 담을 리스트 초기화
        all_ohlcv = []
        # 데이터를 가져오기
        while start_time < end_time:
            ohlcv = self.exchange.fetch_ohlcv(self.symbol, '1m', since=start_time, limit=1000)
            if not ohlcv:
                break
            start_time = ohlcv[-1][0] + 1
            all_ohlcv.extend(ohlcv)
            # time.sleep(1)

        df = pd.DataFrame(all_ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
        df.set_index('datetime', inplace=True)

        if not self.df.empty and not df.empty:
            print(self.df.index[-1], "/", df.index[-1])
            if self.df.index[-1] == df.index[-1]:
                self.df.update(df)
            else:
                # 업데이트하고 빠진 부분은 추가
                self.df = self.df.combine_first(df)
                
        return self.df
    
    def get_ohlc(self):
        return self.get_ohlcv()[['open', 'high', 'low', 'close']]
    
    def get_volume(self):
        return self.get_ohlcv()['volume'].to_frame()
    
    def get_ohlc_json(self, timeframe='5T',  limit=100):
        df = self.df.copy()
        # resample로 timeframe에 맞게 데이터를 재배열
        df = df.resample(timeframe).agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'})
        df['time'] = df.index.astype('int64') // 10 ** 9
        res = json.loads(df[['time', 'open', 'high', 'low', 'close']].tail(limit).to_json(
            orient='records'))
        # timelist = pd.date_range(df.index[-1], freq=timeframe, periods=31, unit='s').tolist()[1:]
        # for t in timelist:
        #     res.append({'time': t.value // 10 ** 9})
        # pprint(res)
        return res

    def get_volume_json(self, timeframe='5T', limit=100):
        df = self.df.copy()
        df = df.resample(timeframe).agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})
        df['time'] = df.index.astype('int64') // 10 ** 9
        df['value'] = df['volume'].astype('float') * 1000
        df['color'] = np.where(df['close'] > df['open'], 'rgba(0, 150, 136, 0.5)', 'rgba(255,82,82, 0.5)')
        res = json.loads(df[['time', 'value', 'color']].tail(limit).to_json(
            orient='records'))
        # timelist = pd.date_range(df.index[-1], freq=timeframe, periods=31, unit='s').tolist()[1:]
        # for t in timelist:
        #     res.append({'time': t.value // 10 ** 9, 'value': 0, 'color': 'rgba(0, 150, 136, 0.5)'})
        # # pprint(res)
        return res

    def get_yhat_json(self, timeframe='15T', outtf = '5T', limit=1000):
        df = self.df.copy()
        df = df.resample(timeframe).agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'})
        df['ds'] = df.index
        df['y'] = df['close']
        df = df[['ds', 'y']].tail(limit)
        m = Prophet(interval_width=0.9)
        m.fit(df)
        future = m.make_future_dataframe(periods=10, freq=timeframe)
        forecast = m.predict(future)
        forecast.set_index('ds', inplace=True)
        forecast = forecast.resample(outtf).agg({'yhat': 'first', 'yhat_lower': 'first', 'yhat_upper': 'first'})
        forecast = forecast.interpolate()
        # print(forecast)
        forecast['time'] = forecast.index.astype('int64') // 10 ** 9
        forecast['value'] = forecast['yhat'].astype('float')
        res1 = json.loads(forecast[['time', 'value']].tail(limit+1000).to_json(orient='records'))
        forecast['value'] = forecast['yhat_lower'].astype('float')
        res2 = json.loads(forecast[['time', 'value']].tail(limit+1000).to_json(orient='records'))
        forecast['value'] = forecast['yhat_upper'].astype('float')
        res3 = json.loads(forecast[['time', 'value']].tail(limit+1000).to_json(orient='records'))
        # pprint(res1)
        return (res1, res2, res3)
    
if __name__ == '__main__':
    data = BitgetData('BTC/USDT:USDT')
    while True:
        time.sleep(3)
        start = time.time()
        # pprint(data.get_ohlc_json())
        data.get_yhat_json()
        print(time.time() - start)
