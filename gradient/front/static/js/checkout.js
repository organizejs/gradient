/**
 ** Checkout dynamic image sizing
 ** Called from templates/checkout.html
 **/
function resize_images() {
  $('.cart-item-image').each(function() {
    var img = $(this).find('img')
    var height = img.attr('height');
    var width = img.attr('width');
    if (height > width) {
      img.css({
        'height': '100%',
        'width': 'auto'
      })
    } else {
      img.css({
        'width': '100%',
        'height': 'auto'
      })
    }
  });
};

/**
 ** Stripe Checkout
 ** Called from templates/checkout.html
 **/
function stripe_checkout(
    key,
    pay_url,
    transaction_id,
    transaction_total,
    pay_selector) {

  var handler = StripeCheckout.configure({
    key: key,
    name: 'Gradient',
    locale: 'auto',
    description: 'Gradient Checkout',
    billingAddress: true,
    allowRememberMe: true,
    token: function(token, args) {
      var form = document.createElement('form');
      form.setAttribute('method', 'POST');
      form.setAttribute('action', pay_url);

      var field = document.createElement('input');
      field.setAttribute('type', 'hidden');
      field.setAttribute('name', 'txid');
      field.setAttribute('value', transaction_id);
      form.appendChild(field);

      field = document.createElement('input');
      field.setAttribute('type', 'hidden');
      field.setAttribute('name', 'token');
      field.setAttribute('value', token.id);
      form.appendChild(field);

      document.body.appendChild(form);
      form.submit();
    }
  });

  $(pay_selector).on('click', function() {
    handler.open({
      amount: transaction_total
    });
  });

};
