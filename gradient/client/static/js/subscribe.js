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
