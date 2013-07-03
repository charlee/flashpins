
// django csrftoken
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        var csrftoken = $.cookie('csrftoken');
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});



$(document).ready(function() {

  // init the pin dialog
  $("#pin-dialog").pinDialog();

  // Pin-add button
  $("#btn-pin").click(function() {
    $("#pin-dialog").pinDialog("open", "new");
  });

  // pin edit link
  $("a.pin-edit").click(function() {
    $("#pin-dialog").pinDialog("open", "edit", { id: parseInt($(this).attr("pin_id")) });
    return false;
  });


  // init the login and sign up link
  $("#login-dialog").loginDialog();
  $("#signup-dialog").signupDialog();

  $("#btn-login").click(function() {
    $("#login-dialog").loginDialog("open");
    return false;
  });

  $("#btn-signup").click(function() {
    $("#signup-dialog").signupDialog("open");
    return false;
  });

  // save an existing link to pin
  $("a.pin-save").click(function() {
    $("#pin-dialog").pinDialog("open", "pin", { id: parseInt($(this).attr("link_id")) });
    return false;
  });
});
