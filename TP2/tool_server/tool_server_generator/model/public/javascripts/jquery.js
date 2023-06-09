function open_sidebar() {
  document.getElementById("main").style.marginLeft = "25%";
  document.getElementById("sidebar").style.width = "25%";
  document.getElementById("sidebar").style.display = "block";
  document.getElementById("nav").style.display = 'none';
}
function close_sidebar() {
  document.getElementById("main").style.marginLeft = "0%";
  document.getElementById("sidebar").style.display = "none";
  document.getElementById("nav").style.display = "inline-block";
}

function open_tools(id) {
  var x = document.getElementById(id);
  if (x.className.indexOf("w3-show") == -1) {
    x.className += " w3-show";
    x.previousElementSibling.className += " secondary_bg_color secondary_text_color";
  } else { 
    x.className = x.className.replace(" w3-show", "");
    x.previousElementSibling.className = 
    x.previousElementSibling.className.replace(" secondary_bg_color secondary_text_color", "");
  }
}