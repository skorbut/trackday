var socket = io.connect(
  location.protocol + '//' + document.domain + ':' + location.port + '/pit_events',
  {
    upgrade: false,
    transports: ['websocket']});
    socket.on('connect', function() {
        socket.emit('pit_events', {data: 'I\'m connected!'});
  }
);

socket.on('pit_status', function(msg) {
  console.log("Pit status: " + msg);
  var pit_status = JSON.parse(msg);
  pit_status.forEach(function(in_pit, index) {
    var selector = $("#gas-pump-" + index + " i")
    if (selector.length > 0) {
      if(in_pit) {
        selector.addClass('in-pit')
      } else {
        selector.removeClass('in-pit')
      }
    }
  });
});
