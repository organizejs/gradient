// Function used to add card to stripe 
// TODO figure out how to validate address details
//      in the add_card_form

function stripe_add_card(
    stripe_key,
    card_element_selector,
    card_error_selector,
    card_form_id,
    card_details,
    next_page_url) {

  var stripe = Stripe(stripe_key);
  var elements = stripe.elements();
  
  // Create an instance of the card Element.
  var card = elements.create('card', {
    hidePostalCode: true,
    style: {
      base: {
        iconColor: '#666EE8',
        color: '#31325F',
        lineHeight: '2.5em',
        fontWeight: 300,
        fontSize: '1.0em',
        '::placeholder': {
          color: '#CFD7E0',
        },
      },
    }
  });

  // Add an instance of the card Element into the `card-element` <div>.
  card.mount(card_element_selector);

  card.addEventListener('change', function(event) {
    var displayError = $(card_error_selector);
    if (event.error) {
      displayError.html(event.error.message);
    } else {
      displayError.html('');
    }
  });

  // Create a token or display an error when the form is submitted.
  var form = document.getElementById(card_form_id);
  form.addEventListener('submit', function(event) {
    event.preventDefault();

    var options = {
      name: document.getElementById(card_details.name_id).value,
      address_line1: document.getElementById(card_details.address.line_1_id).value,
      address_line2: document.getElementById(card_details.address.line_2_id).value,
      address_city: document.getElementById(card_details.address.city_id).value,
      address_state: document.getElementById(card_details.address.state_id).value,
      address_zip: document.getElementById(card_details.address.zip_id).value,
      address_country: document.getElementById(card_details.address.country_id).value,
    };

    stripe.createToken(card, options).then(function(result) {
      if (result.error) {
        // Inform the customer that there was an error.
        var errorElement = $(card_error_selector);
        errorElement.html(result.error.message);
      } else {
        // Send the token to your server.
        stripeTokenHandler(result.token);
      }
    });
  });

  function stripeTokenHandler(token) {
    // Insert the token ID into the form so it gets submitted to the server
    var form = document.getElementById(card_form_id);

    var hiddenInput = document.createElement('input');
    hiddenInput.setAttribute('type', 'hidden');
    hiddenInput.setAttribute('name', 'token');
    hiddenInput.setAttribute('value', token.id);
    form.appendChild(hiddenInput);

    hiddenInput = document.createElement('input');
    hiddenInput.setAttribute('type', 'hidden');
    hiddenInput.setAttribute('name', 'next');
    hiddenInput.setAttribute('value', next_page_url);
    form.appendChild(hiddenInput);

    // Submit the form
    form.submit();
  }

}
