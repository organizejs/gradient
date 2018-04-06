from tests import Base, factory
from gradient.product import Product
from gradient.transaction import Transaction


class TransactionTest(Base):
    def test_customer(self):
        customer = factory.create_customer(self.app)
        transaction = Transaction(customer=customer)
        self.db.session.add(transaction)
        self.db.session.commit()
        self.assertEqual(transaction.customer, customer)
        self.assertEqual(customer.transactions, [transaction])

    def test_add_products(self):
        customer = factory.create_customer(self.app)
        transaction = Transaction(customer=customer)
        product1 = Product(sku='A')
        product2 = Product(sku='B')
        transaction.add_product(product1, 10, 20)
        transaction.add_product(product2, 10, 20)
        self.db.session.add(transaction)
        self.db.session.commit()
        self.assertEqual(transaction.products, [product1, product2])
        self.assertEqual(product1.transactions, [transaction])
        self.assertEqual(product2.transactions, [transaction])

    def test_multiple_transactions_per_product(self):
        customer = factory.create_customer(self.app)
        product1 = Product(sku='A')
        product2 = Product(sku='B')

        for _ in range(2):
            transaction = Transaction(customer=customer)
            transaction.add_product(product1, 10, 20)
            transaction.add_product(product2, 10, 20)
            self.db.session.add(transaction)
            self.db.session.commit()

        transactions = Transaction.query.all()
        self.assertEqual(product1.transactions, transactions)
        self.assertEqual(product2.transactions, transactions)

    def test_price(self):
        customer = factory.create_customer(self.app)
        product1 = Product(sku='A')
        product2 = Product(sku='B')
        transaction = Transaction(customer=customer)
        transaction.add_product(product1, 2, 20)
        transaction.add_product(product2, 3, 20)
        self.assertEqual(transaction.total, 5)

    def test_status(self):
        customer = factory.create_customer(self.app)

        for status in Transaction.Status:
            transaction = Transaction(
                customer=customer,
                status=status)
            self.db.session.add(transaction)
            self.db.session.commit()

        transaction = Transaction.query.all()
        self.assertEqual(transaction[0].status.name, 'OPEN')
        self.assertEqual(transaction[1].status.name, 'SUCCESS')
        self.assertEqual(transaction[2].status.name, 'FAILURE')
