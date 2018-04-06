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


