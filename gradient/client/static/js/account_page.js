/**
 ** This page contains the logic for vendor/customer account pages
 **/
function setup_account() {
  if (is_mobile()) {
    // set up nav bar
    var side_pane = $("#account-side-pane")
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

 
