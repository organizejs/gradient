$(document).ready(function() {
  /**
   ** is_mobile function
   **/
  function is_mobile() {
    return $('#mobile-indicator').is(':visible');
  }
  
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
