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

//Retrieve GET variables from the current URL
function getUrlVars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
        vars[key] = value;
    });
    return vars;
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

// Strip duplicate URL paramters
// https://stackoverflow.com/questions/31075133/strip-duplicate-parameters-from-the-url
function stripUrlParams(url, parameter) {
    //prefer to use l.search if you have a location/link object
    var urlparts= url.split('?');
    if (urlparts.length>=2) {

        var stuff = urlparts[1];
        pars = stuff.split("&");
        var comps = {};
        for (i = pars.length - 1; i >= 0; i--)
        {
            spl = pars[i].split("=");
            comps[spl[0]] = spl[1];
        }
        pars = [];
        for (var a in comps)
            pars.push(a + "=" + comps[a]);
        url = urlparts[0] + '?' + pars.join('&');
        return url;
    } else {
        return url;
    }
}

function removeParam(key, sourceURL) {
    var rtn = sourceURL.split("?")[0],
        param,
        params_arr = [],
        queryString = (sourceURL.indexOf("?") !== -1) ? sourceURL.split("?")[1] : "";
    if (queryString !== "") {
        params_arr = queryString.split("&");
        for (var i = params_arr.length - 1; i >= 0; i -= 1) {
            param = params_arr[i].split("=")[0];
            if (param === key) {
                params_arr.splice(i, 1);
            }
        }
        rtn = rtn + "?" + params_arr.join("&");
    }
    return rtn;
}

// Add a parameter to the current page's URL and refresh the page
function addParam(param,url) {
  return stripUrlParams(url + "&" + param);
}

// Open a log file
function viewLogFile(e) {
  $.ajax({
    type        : "get",
    url         : "/errors/errorlog/"+e,
    data        : JSON.stringify({}),
    dataType    : "json",
    contentType : "application/json",
    cache       : false,
    processData : false
  });
}

//Retrieve in messages regarding background jobs and display them as toasts
function getMessages(ignore=false) {
  $.ajax({
      type        : "post",
      url         : "/api/getmessages",
      data        : JSON.stringify({}),
      dataType    : "json",
      contentType : "application/json",
      cache       : false,
      processData : false,
      success: function (rjson) {
        if (ignore) {
          return; //Basically a way to clear messages without displaying them
        }
        for (var i = 0; i < rjson["messages"].length; i++) {
          toastr.info(rjson["messages"][i]);
        }
      }
  });
}

// Register an event handler for receiving messages for background tasks
function listenForMessages() {
  getMessages();
  window.setInterval(getMessages, 5000);
}
