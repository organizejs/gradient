from tests import Base
from gradient.user import User, Role
from gradient.customer import Customer


class CustomerTests(Base):
    def test_create(self):
        user = User(
            email='test@hellovelocity.com',
            password='test',
            active=True)
        customer = Customer(
            user=user,
            individual_income=100,
            household_income=100,
            first_name='some_firstname',
            last_name='some_lastname',
            marital_status=0,
            dependents=1)
        role = Role()
        user.role = role
        self.db.session.add(user)
        self.db.session.commit()

        role = Role.query.first()
        user = User.query.first()
        customer = Customer.query.first()
        self.assertEqual(user.role, role)
        self.assertEqual(user.account, customer)
        self.assertEqual(customer.individual_income, 100)
        self.assertEqual(customer.dependents, 1)
        self.assertEqual(customer.user, user)

    def test_register(self):
        self.assertEqual(User.query.count(), 0)
        self.assertEqual(Customer.query.count(), 0)

        data = {
            'email': 'test@test.com',
            'password': 'password',
            'password_confirm': 'password',
            'first_name': 'Foo',
            'last_name': 'Bar',
            'individual_income': 0,
            'household_income': 0,
            'dependents': 0,
            'marital_status': 0,
            'signature': 'x'
        }
        self.client.post('/c/register', data=data)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(Customer.query.count(), 1)

        user = User.query.first()
        self.assertEqual(user.email, 'test@test.com')
        self.assertEqual(user.account.first_name, 'Foo')

    def test_register_household_income_married(self):
        self.assertEqual(User.query.count(), 0)
        self.assertEqual(Customer.query.count(), 0)

        data = {
            'email': 'test@test.com',
            'password': 'password',
            'password_confirm': 'password',
            'first_name': 'Foo',
            'last_name': 'Bar',
            'individual_income': 0,
            'household_income': None,
            'dependents': 0,
            'marital_status': 1,
            'signature': 'x'
        }
        self.client.post('/register', data=data)
        self.assertEqual(User.query.count(), 0)
        self.assertEqual(Customer.query.count(), 0)

    def test_register_household_income_not_married(self):
        self.assertEqual(User.query.count(), 0)
        self.assertEqual(Customer.query.count(), 0)

        data = {
            'email': 'test@test.com',
            'password': 'password',
            'password_confirm': 'password',
            'first_name': 'Foo',
            'last_name': 'Bar',
            'individual_income': 0,
            'dependents': 0,
            'marital_status': 0,
            'signature': 'x'
        }
        self.client.post('/c/register', data=data)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(Customer.query.count(), 1)

