var socket = io.connect(
  location.protocol + '//' + document.domain + ':' + location.port + '/control_unit_events',
  {
    upgrade: false,
    transports: ['websocket']
  }
);

socket.on('connect', function() {
    socket.emit('control_unit_events', {data: 'I\'m connected!'});
});

socket.on('status', function(msg) {
    console.log("CU status: " + msg);
    selector = $("#cu-status")
    if(msg.startsWith("connected")) {
      selector.removeClass('red')
      selector.removeClass('grey')
      selector.addClass('green')
    } else if (msg.startsWith("not_connected")) {
      selector.removeClass('green')
      selector.removeClass('grey')
      selector.addClass('red')
    } else if (msg.startsWith("timeout")) {
      selector.removeClass('green')
      selector.removeClass('grey')
      selector.addClass('red')
    }
    } else {
      selector.removeClass('green')
      selector.removeClass('red')
      selector.addClass('grey')
    }
});
