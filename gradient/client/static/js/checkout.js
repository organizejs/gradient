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
 ** Submit form to route /checkout/pay
 **/
function stripe_checkout(pay_url, pay_selector) {

  // pay
  $(pay_selector).on('click', function() {

    var form = document.createElement('form');
    form.setAttribute('method', 'POST');
    form.setAttribute('action', pay_url);

    var field = document.createElement('input');
    field.setAttribute('type', 'hidden');
    field.setAttribute('name', 'card_id');
    field.setAttribute('value', $("#select-card").val());
    form.appendChild(field);

    document.body.appendChild(form);
    form.submit();
  });

};
