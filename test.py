import keyring
import mojito
import pprint

irp_api_key = keyring.get_password("irp_api_key", "birdblues")
irp_api_secret = keyring.get_password("irp_api_secret", "birdblues")

api_key = keyring.get_password("isa_api_key", "birdblues")
api_secret = keyring.get_password("isa_api_secret", "birdblues")

key = api_key
secret = api_secret
acc_no_1 = "64012548-22" # 연금저축 1
acc_no_2 = "64267316-22" # 연금저축 2
acc_no_isa = "64043278-01" # ISA
acc_no_0 = "63981494-01" # 위탁
acc_no_irp = "64012548-29" # IRP
mock = False

broker = mojito.KoreaInvestment(
    api_key=key,
    api_secret=secret,
    acc_no=acc_no_isa,
    mock=mock,
    exchange='서울'
)
print(broker)

# balance = broker.fetch_balance_domestic_irp('', '20240701', '20240710')
# balance = broker.fetch_balance()
# pprint.pprint(balance)

profit = broker.fetch_profit("20240101", "20240712")
pprint.pprint(profit)