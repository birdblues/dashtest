import keyring

api_key = keyring.get_password("irp_api_key", "birdblues")
api_secret = keyring.get_password("irp_api_secret", "birdblues")

