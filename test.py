import keyring
import mojito
import pprint

api_key = keyring.get_password("irp_api_key", "birdblues")
api_secret = keyring.get_password("irp_api_secret", "birdblues")

key = api_key
secret = api_secret
acc_no = "64012548-22"
mock = False

broker = mojito.KoreaInvestment(
    api_key=key,
    api_secret=secret,
    acc_no=acc_no,
    mock=mock,
    exchange='서울'
)
print(broker)

balance = broker.fetch_balance_domestic_test('', '20231201', '20240102')
pprint.pprint(balance)