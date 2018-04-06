from tests import Base
from gradient.user import User
from gradient.vendor import Vendor


class VendorTests(Base):
    def test_create(self):
        user = User(
            email='test@hellovelocity.com',
            password='test',
            active=True)
        vendor = Vendor(
            user=user,
            stripe_pk='foo',
            stripe_sk='bar',
            slug='test')
        self.db.session.add(vendor)
        self.db.session.commit()

        user = User.query.first()
        vendor = Vendor.query.first()
        self.assertEqual(user.account, vendor)
        self.assertEqual(vendor.slug, 'test')
        self.assertEqual(vendor.user, user)

