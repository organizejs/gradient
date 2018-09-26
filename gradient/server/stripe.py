import stripe

class StripeClient():
  client = None
  connect_client_id = None
  secret_key = None

  def __init__(self):
    self.client = stripe
    
  def set_secret_key(self, secret_key: str):
    self.secret_key = secret_key
    self.client.api_key = secret_key

  def set_connect_id(self, connect_client_id: str):
    self.connect_client_id = connect_client_id

stripe = StripeClient()


