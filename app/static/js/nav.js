// https://www.w3schools.com/howto/howto_js_sidenav.asp

/* Set the width of the side navigation to 250px and the left margin of the page content to 250px */
function openSideNav() {
  var sidenav        = $("#mySidenav");
  sidenav.addClass("open");
  var closebtn       = sidenav.find('.closebtn')[0];
  closebtn.innerHTML = "&times;";
  closebtn.onclick   = closeSideNav;
}

/* Set the width of the side navigation to 0 and the left margin of the page content to 0 */
function closeSideNav() {
  var sidenav        = $("#mySidenav");
  sidenav.removeClass("open");
  var closebtn       = sidenav.find('.closebtn')[0];
  closebtn.innerHTML = "&rarr;";
  closebtn.onclick   = openSideNav;
}
