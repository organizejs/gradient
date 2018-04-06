from tests import Base, factory
from gradient.checkout.routes import price


MAX_PRICE = 100


class PriceTests(Base):
    def setUp(self):
        vendor = factory.create_vendor(self.app)
        vendor.max_income = 10000
        vendor.min_income = 50000
        vendor.min_price = 0.8
        self.db.session.add(vendor)
        self.db.session.commit()
        self.vendor = vendor

    def test_min_price(self):
        customer = factory.create_customer(self.app)
        customer.individual_income = 0
        gprice = price(customer, self.vendor, MAX_PRICE)
        self.assertEqual(gprice, 80)

    def test_max_price(self):
        customer = factory.create_customer(self.app)
        customer.individual_income = 1000000
        gprice = price(customer, self.vendor, MAX_PRICE)
        self.assertEqual(gprice, 100)

    def test_price(self):
        customer = factory.create_customer(self.app)
        customer.individual_income = 20000
        gprice = price(customer, self.vendor, MAX_PRICE)
        self.assertEqual(gprice, 85)

        customer = factory.create_customer(self.app)
        customer.individual_income = 30000
        gprice = price(customer, self.vendor, MAX_PRICE)
        self.assertEqual(gprice, 90)
