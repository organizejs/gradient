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
