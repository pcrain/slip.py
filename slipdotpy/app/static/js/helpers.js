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
function travel(path,resetPages=true) {
  href = URL_add_parameter(location.href,"path",path);
  if (resetPages) {
    href = removeParam("page",href);
    href = removeParam("prevpage",href);
    href = removeParam("nextpage",href);
  }
  location.href = href;
}

//Refresh the page after adding a parameter
function select(path) {
  location.href = URL_add_parameter(location.href,"file",path);
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
              getMessages(true);
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

// Ensure there is a ? in the url
function ensureQuery(url) {
  var urlparts= url.split('?');
  if (urlparts.length>=2) {
    return url;
  }
  var urlparts= url.split('&');
  if (urlparts.length==1) {
    return url;
  }
  var url = urlparts[0]+"?submit=submit";
  for(var i = 1; i < urlparts.length; i++) {
    url += "&"+urlparts[i];
  }
  return url;
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

// Sort items in a table
// https://www.w3schools.com/howto/howto_js_sort_table.asp
function sortTable(tid,n,dir="asc",sort="num") {
  var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
  odir = dir;
  table = document.getElementById(tid);
  switching = true;

  // Set headers
  heads = table.rows[0].getElementsByTagName("TH");
  for(i = 0; i < heads.length; i++) {
    heads[i].classList.remove("rev");
    heads[i].classList.remove("asc");
    heads[i].classList.remove("desc");
    if (i == n) {
      heads[i].classList.add("sorted");
      heads[i].classList.add(dir);
    } else {
      heads[i].classList.remove("sorted");
    }
  }
  /* Make a loop that will continue until
  no switching has been done: */
  while (switching) {
    // Start by saying: no switching is done:
    switching = false;
    rows = table.rows;
    /* Loop through all table rows (except the
    first, which contains table headers): */
    for (i = 1; i < (rows.length - 1); i++) {
      // Start by saying there should be no switching:
      shouldSwitch = false;
      /* Get the two elements you want to compare,
      one from current row and one from the next: */
      x = rows[i].getElementsByTagName("TD")[n];
      y = rows[i + 1].getElementsByTagName("TD")[n];
      /* Check if the two rows should switch place,
      based on the direction, asc or desc: */
      if (sort == "num") {  //numeric sort
        if (dir == "asc") {
          if (+x.innerHTML > +y.innerHTML) {
            // If so, mark as a switch and break the loop:
            shouldSwitch = true;
            break;
          }
        } else if (dir == "desc") {
          if (+x.innerHTML < +y.innerHTML) {
            // If so, mark as a switch and break the loop:
            shouldSwitch = true;
            break;
          }
        }
      } else {  //string sort
        if (dir == "asc") {
          if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
            // If so, mark as a switch and break the loop:
            shouldSwitch = true;
            break;
          }
        } else if (dir == "desc") {
          if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
            // If so, mark as a switch and break the loop:
            shouldSwitch = true;
            break;
          }
        }
      }
    }
    if (shouldSwitch) {
      /* If a switch has been marked, make the switch
      and mark that a switch has been done: */
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
      // Each time a switch is done, increase this count by 1:
      switchcount ++;
    } else {
      /* If no switching has been done AND the direction is "asc",
      set the direction to "desc" and run the while loop again. */
      if (switchcount == 0 && dir == odir) {
        dir = (odir == "asc") ? "desc" : "asc";
        heads[n].classList.add("rev");
        heads[n].classList.add(dir);
        heads[n].classList.remove(odir);
        switching = true;
      }
    }
  }
}


// Nice tooltips modified from: https://css-tricks.com/bubble-point-tooltips-with-css3-jquery/
// IIFE to ensure safe use of $
(function( $ ) {

  // Create plugin
  $.fn.tooltips = function(el) {

    // var mousex = -1;
    // var mousey = -1;

    // $(document).mousemove(function(event) {
    //     mousex = event.pageX;
    //     mousey = event.pageY;
    // });

    var $tooltip,
      $body = $('body'),
      $el;

    // Ensure chaining works
    return this.each(function(i, el) {

      $el = $(el).attr("data-tooltip", i);

      // Make DIV and append to page
      // Arrow version
      // var $tooltip = $('<div class="tooltip" data-tooltip="' + i + '">' + $el.attr('title') + '<div class="arrow"></div></div>').appendTo("body");
      // No arrow version
      var $tooltip = $('<div class="tooltip" data-tooltip="' + i + '">' + $el.attr('title') + '</div>').appendTo("body");

      // Position right away, so first appearance is smooth
      var linkPosition = $el.position();

      $tooltip.css({
        top: linkPosition.top - $tooltip.outerHeight()/2,
        left: linkPosition.left - ($tooltip.width()/2)
      });

      $el
      // Get rid of yellow box popup
      .removeAttr("title")

      // Mouseenter
      .hover(function(e) {

        var evx = e.pageX;
        var evy = e.pageY;
        var ww  = window.innerWidth;
        var wh  = window.innerHeight;

        $el = $(this);

        $tooltip = $('div[data-tooltip=' + $el.data('tooltip') + ']');

        // Reposition tooltip, in case of page movement e.g. screen resize
        var linkPosition = $el.position();

        $tooltip.css({
          top:  evy - ((evy > wh/2) ? $tooltip.outerHeight()+24 : -24),
          left: evx - ((evx > ww/2) ? $tooltip.outerWidth()     :   0)
        });

        // Adding class handles animation through CSS
        $tooltip.addClass("active");

        // Mouseleave
      }, function(e) {

        $el = $(this);

        // Temporary class for same-direction fadeout
        $tooltip = $('div[data-tooltip=' + $el.data('tooltip') + ']').addClass("out");

        // Remove all classes
        // $tooltip.removeClass("active").removeClass("out");
        $tooltip.removeClass("active").removeClass("out");

        });

      });

    }

})(jQuery);
