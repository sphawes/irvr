window.onload = function() {
        var s = new WebSocket("ws://localhost:900/");
        s.onopen = function(e) { alert("opened"); }
        s.onclose = function(e) { alert("closed"); }
        s.onmessage = function(e) { alert("got: " + e.data); }
      };
