var socket = io.connect(
  location.protocol + '//' + document.domain + ':' + location.port + '/startlight_events',
  {
    upgrade: false,
    transports: ['websocket']
  }
);

socket.on('connect', function() {
    socket.emit('startlight_events', {data: 'I\'m connected!'});
});

socket.on('startlight_status', function(startlight_status) {
    console.log("startlight status: " + startlight_status);
    switch (startlight_status) {
      case 0 :
        for(var i=0; i < 6; i++){
          var selector = $("#startlight-" + i)
          selector.removeClass('red')
          selector.removeClass('grey')
          selector.addClass('green')
        }
        break;
      case 1 :
        for(var i=0; i < 6; i++){
          var selector = $("#startlight-" + i)
          selector.removeClass('green')
          selector.addClass('grey')
          selector.removeClass('red')
        }
        break;
      case 2 :
        for(var i=0; i <= 1; i++){
          var selector = $("#startlight-" + i)
          selector.removeClass('green')
          selector.removeClass('grey')
          selector.addClass('red')
        }
        for(var i=1; i < 6; i++){
          var selector = $("#startlight-" + i)
          selector.removeClass('green')
          selector.addClass('grey')
          selector.removeClass('red')
        }
        break;
      case 3 :
        for(var i=0; i <= 2; i++){
          var selector = $("#startlight-" + i)
          selector.removeClass('green')
          selector.removeClass('grey')
          selector.addClass('red')
        }
        for(var i=2; i < 6; i++){
          var selector = $("#startlight-" + i)
          selector.removeClass('green')
          selector.addClass('grey')
          selector.removeClass('red')
        }
        break;
      case 4 :
        for(var i=0; i <= 3; i++){
          var selector = $("#startlight-" + i)
          selector.removeClass('grey')
          selector.removeClass('green')
          selector.addClass('red')
        }
        for(var i=3; i < 6; i++){
          var selector = $("#startlight-" + i)
          selector.removeClass('green')
          selector.addClass('grey')
          selector.removeClass('red')
        }
        break;
      case 5 :
        for(var i=0; i <= 4; i++){
          var selector = $("#startlight-" + i)
          selector.removeClass('grey')
          selector.removeClass('green')
          selector.addClass('red')
        }
        for(var i=4; i < 6; i++){
          var selector = $("#startlight-" + i)
          selector.removeClass('startlight-green')
          selector.addClass('startlight-grey')
          selector.removeClass('startlight-red')
        }
        break;
      case 6 :
        for(var i=0; i <= 5; i++){
          var selector = $("#startlight-" + i)
          selector.removeClass('startlight-grey')
          selector.removeClass('startlight-green')
          selector.addClass('startlight-red')
        }
        break;
      case 7 :
        for(var i=0; i < 6; i++){
          var selector = $("#startlight-" + i)
          selector.removeClass('startlight-red')
          selector.removeClass('startlight-green')
          selector.addClass('startlight-grey')
        }
        break;
    }
});
