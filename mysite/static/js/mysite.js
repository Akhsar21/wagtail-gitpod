$(function () {
  // fix menu when passed
  $(".masthead").visibility({
    once: false,
    onBottomPassed: function () {
      $(".fixed.menu").transition("fade in");
    },
    onBottomPassedReverse: function () {
      $(".fixed.menu").transition("fade out");
    },
  });

  $(".special.card .image").dimmer({
    on: "hover",
  });
  $(".star.rating").rating();

  $(".card .dimmer").dimmer({
    on: "hover",
  });

  // create sidebar and attach to menu open
  $(".ui.sidebar").sidebar("attach events", ".toc.item");

  $("input").prop("required", false);

  $("textarea").prop("required", false);

  $(".ui.radio.checkbox").checkbox();
});

//   (document).ready

// To top
window.addEventListener("scroll", () => {
  const toTop = document.querySelector(".to-top");
  if (window.pageYOffset > 100) {
    toTop.classList.add("active");
  } else {
    toTop.classList.remove("active");
  }
});
