csvfile = 'bitget_ohlcv.csv'

import ccxt
import pandas as pd
import pytz
import time

# Bitget API 키 설정
api_key = 'bg_8a663c5d219e63b76279751204869dfc'
api_secret = 'fbde1ec10e3de9022574844d33600097d84fe9eab7cfd2f82ab6c33b0b96e4fb'
api_passphrase = 'korea111'

exchange = ccxt.bitget({
    'apiKey': api_key,
    'secret': api_secret,
    'password': api_passphrase,
    'options': {
            'defaultType': 'future',
    },
    'verbose': False,
    })

# 시간 설정
end_time = exchange.milliseconds()
start_time = end_time - 30 * 24 * 60 * 60 * 1000

# 데이터를 담을 리스트 초기화
all_ohlcv = []

# 데이터를 가져오기
while start_time < end_time:
    #밀리세컨드를 datetime으로 변경
    print(pd.to_datetime(start_time, unit='ms'))
    print(pd.to_datetime(end_time, unit='ms'))
    ohlcv = exchange.fetch_ohlcv('BTC/USDT', '1m', since=start_time, limit=1000)
    print(ohlcv)
    df = pd.DataFrame(ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
    print(df)
    if not ohlcv:
        break
    start_time = ohlcv[-1][0] + 1
    all_ohlcv.extend(ohlcv)
    time.sleep(1)

df = pd.DataFrame(all_ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')

df.set_index('datetime', inplace=True)
df.to_csv(csvfile)
print(df)