from ..product import Product


class CartItem():

  def __init__(self, product, quantity):
    self.product = product
    self.quantity = int(quantity)

  def __repr__(self):
    return "CartItem(product_sku('%s'), quantity(%i))"%(self.product.sku, self.quantity)


class Cart():

  def __init__(self, vendor: 'Vendor'):
    self.items = [] # [CartItems]
    self.vendor = vendor

  def __repr__(self):
    return "Cart(%r)"%([repr(cart_item) for cart_item in self.items])

  def __len__(self):
    '''
    return total quantity in cart
    '''
    return sum([cart_item.quantity for cart_item in self.items])

  def add_product(self, sku: str, quantity: int):
    '''
    check that sku exists, and if so add to cart
    '''
    # check that product exists
    product = Product.query \
      .filter_by(sku=sku, vendor=self.vendor) \
      .first()

    # stop process and throw error if product dne
    if product is None:
      msg = "ERROR: product sku '%s' is not a valid sku for vendor '%s'" % (sku, vendor.company_name)
      print(msg)

    # add product to list of items
    item_not_in_cart = True
    for cart_item in self.items:
      if cart_item.product.sku == sku:
        cart_item.quantity += int(quantity)
        item_not_in_cart = False
     
    if item_not_in_cart:
      cart_item = CartItem(product, quantity)
      self.items.append(cart_item)
