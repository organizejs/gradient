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
        

