// Add a GET parameter to a URL
// https://stackoverflow.com/questions/5997450/append-to-url-and-refresh-page
function URL_add_parameter(url, param, value){
    var hash       = {};
    var parser     = document.createElement('a');

    parser.href    = url;

    var parameters = parser.search.split(/\?|&/);

    for(var i=0; i < parameters.length; i++) {
        if(!parameters[i])
            continue;

        var ary      = parameters[i].split('=');
        hash[ary[0]] = ary[1];
    }

    hash[param] = value;

    var list = [];
    Object.keys(hash).forEach(function (key) {
        list.push(key + '=' + hash[key]);
    });

    parser.search = '?' + list.join('&');
    return parser.href;
}

//Refresh the page after adding a parameter
function travel(path) {
  location.href = URL_add_parameter(location.href,"path",path);
}

//Dummy function for doing nothing
function doNothing() {
    return;
}

//Autoscan function for main page
function autoScan() {
    toastr.info('Beginning autoscan. Page will refresh when complete.')
    var index    = 0;
    var token    = "";
    // var ubutton  = document.getElementById("scan-button");
    // ubutton.disabled = true;

    function checkProgress() {
      $.ajax({
          type        : "post",
          url         : "/api/scan/progress",
          data        : JSON.stringify({"token" : token}),
          dataType    : "json",
          contentType : "application/json",
          cache       : false,
          processData : false,
          success: function (rjson) {
            // ubutton.innerText = "Scanning " + rjson["status"];// first set the value
          },
          complete: function (rjson) {
            if (!("done" in rjson["responseJSON"])) {
              setTimeout(checkProgress, 500);
            } else {
              toastr.success('Scan complete! Refreshing page.');
              setTimeout(function(){location.reload();}, 1000);
              // $("#log-button").prop("disabled",false);
              // $("#log-button").show();
              // $("#log-button").click(function() {
              //   $.ajax({
              //     type        : "get",
              //     url         : "/api/scanlog/"+rjson["responseJSON"]["details"],
              //     data        : JSON.stringify({"token" : token}),
              //     dataType    : "json",
              //     contentType : "application/json",
              //     cache       : false,
              //     processData : false
              //   });
              // });
            }
          }
      });
    }

    $.ajax({
      type        : "post",
      url         : "/api/scan",
      data        : new FormData(),
      contentType : false,
      cache       : false,
      processData : false,
      success     : function(rjson) {
        // ubutton.title      = "Scanning " + JSON.stringify(rjson);
        // ubutton.innerText  = rjson["status"];
        token              = rjson["token"];
        setTimeout(checkProgress, 500);
      },
      error: function(XMLHttpRequest, textStatus, errorThrown) {
        toastr.error('An error occurred during scanning');
        // ubutton.innerText = "Error";
        // ubutton.title     = "Status: " + textStatus+"\nError: " + errorThrown;
      }
    });
}

//Handle refreshes
document.onkeyup = function(e) {
  if (e.which == 116) {
    location.reload();
  }
  // else if (e.ctrlKey && e.altKey && e.which == 89) {
  //   alert("Ctrl + Alt + Y shortcut combination was pressed");
  // }
  // else if (e.ctrlKey && e.altKey && e.shiftKey && e.which == 85) {
  //   alert("Ctrl + Alt + Shift + U shortcut combination was pressed");
  // }
};
