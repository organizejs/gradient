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

/**
 ** This page contains the logic for onboarding a customer
 ** Called from templates/account/customer/onboarding.html
 **/
function customer_onboarding(first_name, last_name) {

  var _sig;
  var _first_name = first_name;
  var _last_name = last_name;
  var _signature_pad = $('#signature-pad');
  var _form_signature = $('[name=signature]');
  var _form_marital_status = $('[name=marital_status]');
  var _form_household_income = $('[name=household_income]');
  var _form_individual_income = $('[name=individual_income]');

  onboarding_util = OnboardingUtil();

  // setup listeners
  onboarding_util.listen_for_next_section(set_user_info);
  onboarding_util.listen_for_navigation(set_user_info);

  // set current to first
  onboarding_util.set_active_section(0);
  
  // set up signature canvas
  setupSignaturePad();
  
  // toggle household income option if user selects married
  toggle_household_income();
  _form_marital_status.on('change', toggle_household_income);


  // setup canvas for signature
  function setupSignaturePad() {
    var signaturePad = new SignaturePad(_signature_pad[0], {
      penColor: '#0000ff',
      onEnd: function() {
        _sig = signaturePad.toDataURL();
        _form_signature.val(_sig);
      }
    });
    signaturePad.fromDataURL(_form_signature.val());
  };


  // Toggle household income field based on marital status value
  function toggle_household_income() {
    var selected = _form_marital_status.find(':selected').val();

    // 0 = not married 
    if (selected == 0) { 
      _form_household_income
        .closest('.onboard-field-wrapper')
        .addClass('disabled');
      _form_individual_income
        .closest('.onboard-field-wrapper')
        .removeClass('disabled');
    } 

    // 1 = married
    else { 
      _form_individual_income
        .closest('.onboard-field-wrapper')
        .addClass('disabled');
      _form_household_income
        .closest('.onboard-field-wrapper')
        .removeClass('disabled');
    }
  };


  function select_text(name, data) {
    var val = data[name];
    return $(`[name=${name}] [value=${val}]`).text();
  };


  function escape(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/>/g, '&gt;')
      .replace(/</g, '&lt;');
  };


  function set_user_info() {
    var data = onboarding_util.get_form_data($('form'));
    console.log(data);

    // TODO - handle the case for household income
    var text = `My name is <b>${escape(_first_name)} ${escape(_last_name)}</b>.
      ${data.individual_income ? 'I, individually, make ' : 'My household makes ' } 
      approximately <b>$${data.individual_income || data.household_income}</b> per year.
      I am currently <b>${escape(select_text('marital_status', data).toLowerCase())}</b>,
      and have <b>${select_text('dependents', data)}</b> ${data.dependents == 1 ? 'dependent' : 'dependents'}.`;

    $('.onboard-confirm-info').html(text);
    $('.onboard-confirm-sig').attr('src', _sig);
  };

};

/**
 ** This page contains the logic for vendor/customer home pages
 **/
function setup_home() {
  if (is_mobile()) {
    // set up nav bar
    var side_pane = $("#home-side-pane")
    side_pane.hide();
    $(".hamburger").click(function() {
      if (side_pane.is(":visible")) {
        side_pane.slideUp();
      } else {
        side_pane.slideDown();
      }
    });
  }
}

 

/**
 ** is_mobile function
 **/
function is_mobile() {
  return $('#mobile-indicator').is(':visible');
}

$(document).ready(function() {
  /**
   ** Mobile navigation
   **/
  const nav_menu_button = $("#nav-menu-button");
  const nav_options_container = $("#nav-options-container");
  const nav_close_button = $("#nav-menu-close");
  
  //if(/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
  if (is_mobile()) {
    // set up nav bar
    nav_options_container.hide();
    $(".hamburger").click(function() {
      if (nav_options_container.is(":visible")) {
        nav_options_container.slideUp();
      } else {
        nav_options_container.slideDown();
      }
    });
  }

  /**
   ** Carousel for explainer slides on the landing page
   **/
  const explainer_array = [{
    slide_el: $('#explainer-slide-1'),
    nav_el: $('#explainer-nav-1'),
    active: true
  }, {
    slide_el: $('#explainer-slide-2'),
    nav_el: $('#explainer-nav-2'),
    active: false
  }, {
    slide_el: $('#explainer-slide-3'),
    nav_el: $('#explainer-nav-3'),
    active: false
  }];


  $(document).ready(function() {
    updateSlides();
    for (i in explainer_array) {
      nav_el = explainer_array[i].nav_el;
      (function(j) {
        nav_el.click(function() {
          setActiveSlide(j);
        });
      })(i);
    }
  });


  function setActiveSlide(i) {
    for (j in explainer_array) { slide = explainer_array[j];
      slide.active = false;
    }
    explainer_array[i].active = true;
    updateSlides();
  };


  function updateSlides() {
    for (i in explainer_array) {
      slide = explainer_array[i]
      if (slide.active) {
        slide.slide_el.addClass("active")
        slide.nav_el.addClass("active")
      } else {
        slide.slide_el.removeClass("active")
        slide.nav_el.removeClass("active")
      }
    }
  };

});

/**
 ** Submit post request when users subscribe (mailchimp)
 ** Called from templates/_newsletter_form.html
 **/
function subscribe_newsletter(
    subscribe_url,
    subscribe_form,
    subscribe_feedback_selector,
    subscribe_submit_selector) {

  subscribe_form.each(function() {
    subscribe_form = $(this);
    subscribe_form_feedback = $(this).find(subscribe_feedback_selector);
    subscribe_form_submit = $(this).find(subscribe_submit_selector);

    (function(
      subscribe_form, 
      subscribe_form_feedback, 
      subscribe_form_submit) {

      subscribe_form.submit(function(e) {
        e.preventDefault();

        fetch(subscribe_url, {
          method: 'POST',
          headers: {  
              "Content-type": "application/x-www-form-urlencoded; charset=UTF-8"  
          },  
          body: subscribe_form.serialize() 
        })
        .then(resp => resp.json())
        .then(function(res) {
          if (res.success == true) {
            subscribe_form_feedback
              .css('color', '#00FF00') // green
              .html("Thank you for subscribing!");

            // disable form submit on success
            subscribe_form_submit.prop('disabled', true);
          } else {
            subscribe_form_feedback
              .css('color', '#FFFF00') // yellow
              .html(res.errors);
          }
        })
        .catch(function(err) {
          console.log(err);
        });

      });
    })(subscribe_form, 
      subscribe_form_feedback, 
      subscribe_form_submit);
  });
};

/**
 ** This page contains the logic for registering a vendor
 ** Called from templates/security/register_vendor.html
 **/
function vendor_register() {

  onboarding_util = OnboardingUtil();

  // set active section to be the first one
  onboarding_util.set_active_section(0);

  // setup listeners
  onboarding_util.listen_for_next_section(set_company_info);
  onboarding_util.listen_for_navigation(set_company_info);

  function set_company_info() {
    var data = onboarding_util.get_form_data($('form'));

    $('#confirm_name').html(data.first_name + ' ' + data.last_name);
    $('#confirm_email').html(data.email);
    $('#confirm_company_name').html(data.company_name);
    $('#confirm_address_street').html(data.street);
    $('#confirm_address_other').html(data.city + ' ' + data.state_code + ', ' + data.zip_code);

    /*
    var text = `<div>First name: ${data.first_name}</div>
                <div>Last name: ${data.last_name}</div>
                <div>Company name: ${data.company_name}</div>
                <div>Address: ${data.street}, ${data.city}, ${data.state_code}, ${data.zip_code}</div>`;

    $('.onboard-confirm-info').html(text)
    */
  };

}
        


var OnboardingUtil = function() {

  // set up listener for 'next page' btn on click
  function listen_for_next_section(cb) {
    // TODO consider changing btn select ro .onboard-next-btn
    $('.onboard-next-section').each(function() {
      var next_button = $(this);

      next_button.on('click', function(ev) {
        var curr_section = $(this).closest('.onboard-section');
        var curr_idx = curr_section.index('.onboard-section');
        _set_active_and_validate(curr_idx + 1, cb);
        return false
      });
    });
  };


  // set up listener for navigation clicks
  function listen_for_navigation(cb) {
    $('.onboard-progress').find('li').on('click', function() {
      idx = $(this).index();
      _set_active_and_validate(idx, cb);
    });
  };


  // Get form data from fields under a given selector
  function get_form_data(el) {
    var data = {};
    el.find('input, select').each(function() {
      var name = $(this).attr('name'),
          val = $(this).val(),
          type = $(this).attr('type');

      // Handle checkboxes and radio fields specially
      if (type === 'checkbox') {
        val = $(this).is(':checked');
      } else if (type === 'radio') {
        ok = $(this).is(':checked');
        if (!ok) return
      }
      data[name] = val;
    });
    return data;
  };


  // Validate a sequence of form sections
  function _validate_sections(start_idx, end_idx, cb) {
    if (start_idx < end_idx) {
      _validate_section(start_idx, function() {
        _validate_sections(start_idx + 1, end_idx, cb);
      });
    } else {
      cb();
    }
  };


  // Validate a form section, if a validation endpoint is specified
  function _validate_section(idx, cb) {
    var section = $('.onboard-section').eq(idx);

    // Get validation endpoint. If none specified, skip
    var endpoint = section.data('validate');
    if (endpoint === undefined) {
      cb();
      return;
    }

    // Extract form section's values
    section.find('.errors').empty();
    var data = get_form_data(section);

    // Validate form data against backend
    $.ajax({
      url: endpoint,
      data: data,
      type: 'POST',
      success: function (data) {
        if (data.success) {
          cb();
        } else {
          // Render errors on fields
          set_active_section(idx);
          $.each(data.errors, function(name, errs) {
            var errEl = $('[name='+name+']')
              .closest('.form-field')
              .find('.errors');
            errEl.empty();
            for(var i=0; i < errs.length; i++) {
              errEl.append(`<li>${errs[i]}</li>`);
            }
          });
        }
      }
    });
  };


  // Set the active form section after validating all previous form sections
  function _set_active_and_validate(idx, cb) {
    var curr_idx = $('.onboard-section-active').index('.onboard-section');
    if (curr_idx < idx) {
      _validate_sections(curr_idx, idx, function() {
        $('.onboard-progress')
          .find('li')
          .eq(curr_idx + 1)
          .addClass('onboard-progress-completed');
        set_active_section(idx, cb);
      });
    } else {
      // If it's a previous form section,
      // go back without validation
      set_active_section(idx, cb);
    }
  };


  // Set active section, without validation
  function set_active_section(idx, cb) {
    // TODO - rename 'onboard-______-active' to just 'active'
    $('.onboard-section-active').hide().removeClass('onboard-section-active');
    $('.onboard-section').eq(idx).show().addClass('onboard-section-active');
    $('.onboard-progress-active').removeClass('onboard-progress-active');
    $('.onboard-progress li').eq(idx).addClass('onboard-progress-active');

    var prompt = $('.onboard-section-active').data('prompt');
    $('.onboard-subtitle').text(prompt);

    if (cb) {
      cb();
    }
  };

  return {
    get_form_data: get_form_data,
    set_active_section: set_active_section,
    listen_for_navigation: listen_for_navigation,
    listen_for_next_section: listen_for_next_section
  }

};


