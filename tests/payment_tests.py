import uuid
from tests import Base, factory
from gradient.vendor import Vendor
from gradient.product import Product
from gradient.transaction import Transaction


class PaymentTests(Base):
    def setUp(self):
        self.customer = factory.create_customer(self.app)
        self.user = self.customer.user
        self.vendor = Vendor(slug='test_vendor', redirect_url='https://google.com')
        self.transaction = Transaction(
            customer=self.customer,
            status=Transaction.Status.OPEN)
        product1 = Product(sku='A', vendor=self.vendor)
        product2 = Product(sku='B', vendor=self.vendor)
        self.transaction.add_product(product1, 50, 100)
        self.transaction.add_product(product2, 80, 200)
        self.db.session.add(self.transaction)
        self.db.session.add(self.vendor)
        self.db.session.commit()

    def test_payment(self):
        self.client.post('/login', data={
            'email': self.user.email,
            'password': self.user.password
        }, follow_redirects=True)

        data = {
            'txid': str(self.transaction.uuid),
            'token': 'tok_visa'
        }
        resp = self.client.post('/checkout/pay', data=data)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual('{}?txid={}&vid={}'.format(
            self.vendor.redirect_url, str(self.transaction.uuid), self.vendor.id),
            resp.location)
        self.assertEqual(self.transaction.status, Transaction.Status.SUCCESS)

    def test_payment_unauthenticated(self):
        data = {
            'txid': str(self.transaction.uuid),
            'token': 'tok_visa'
        }
        resp = self.client.post('/checkout/pay', data=data)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(self.transaction.status, Transaction.Status.OPEN)

    def test_payment_not_owner(self):
        diff_customer = factory.create_customer(self.app)
        diff_user = diff_customer.user
        self.client.post('/login', data={
            'email': diff_user.email,
            'password': diff_user.password
        }, follow_redirects=True)

        data = {
            'txid': str(self.transaction.uuid),
            'token': 'tok_visa'
        }
        resp = self.client.post('/checkout/pay', data=data)
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(self.transaction.status, Transaction.Status.OPEN)

    def test_payment_not_open(self):
        self.client.post('/login', data={
            'email': self.user.email,
            'password': self.user.password
        }, follow_redirects=True)

        status = Transaction.Status.FAILURE
        self.transaction.status = status
        self.db.session.add(self.transaction)
        self.db.session.commit()

        data = {
            'txid': str(self.transaction.uuid),
            'token': 'tok_visa'
        }
        resp = self.client.post('/checkout/pay', data=data)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(self.transaction.status, status)

    def test_payment_nonexistent_transaction(self):
        self.client.post('/login', data={
            'email': self.user.email,
            'password': self.user.password
        }, follow_redirects=True)

        data = {
            'txid': str(uuid.uuid4()),
            'token': 'tok_visa'
        }
        resp = self.client.post('/checkout/pay', data=data)
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(self.transaction.status, Transaction.Status.OPEN)

    def test_payment_bad_token(self):
        self.client.post('/login', data={
            'email': self.user.email,
            'password': self.user.password
        }, follow_redirects=True)

        data = {
            'txid': str(self.transaction.uuid),
            'token': 'foo'
        }
        resp = self.client.post('/checkout/pay', data=data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(self.transaction.status, Transaction.Status.OPEN)

    def test_payment_not_customer(self):
        not_customer = factory.create_vendor(self.app)
        user = not_customer.user
        self.client.post('/login', data={
            'email': user.email,
            'password': user.password
        }, follow_redirects=True)

        data = {
            'txid': str(self.transaction.uuid),
            'token': 'foo'
        }
        resp = self.client.post('/checkout/pay', data=data)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(self.transaction.status, Transaction.Status.OPEN)

    def test_payment_saves_stripe_id(self):
        self.assertIsNone(self.customer.stripe_id)

        self.client.post('/login', data={
            'email': self.user.email,
            'password': self.user.password
        }, follow_redirects=True)

        data = {
            'txid': str(self.transaction.uuid),
            'token': 'tok_visa'
        }
        self.client.post('/checkout/pay', data=data)
        self.assertIsNotNone(self.customer.stripe_id)
