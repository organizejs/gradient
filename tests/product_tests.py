from tests import Base
from gradient.product import Product
from gradient.vendor import Vendor


class ProductTest(Base):
    def test_vendor(self):
        product1 = Product(sku='A')
        product2 = Product(sku='B')
        vendor = Vendor()
        vendor.products = [product1, product2]
        self.db.session.add(vendor)
        self.db.session.commit()

        vendor = Vendor.query.first()
        self.assertEqual(product1.vendor, vendor)
        self.assertEqual(product2.vendor, vendor)
