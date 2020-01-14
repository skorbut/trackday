var socket = io.connect(
  location.protocol + '//' + document.domain + ':' + location.port + '/fuel_events',
  {
    upgrade: false,
    transports: ['websocket']});
    socket.on('connect', function() {
        socket.emit('fuel_events', {data: 'I\'m connected!'});
  }
);
socket.on('fuel_levels', function(msg) {
  console.log("Fuel Levels: " + msg);
  var fuel_levels = JSON.parse(msg);
  fuel_levels.forEach(function(fuel_level, index) {
    for(var i=0; i < 16; i++){
      var selector = $("#fuel-level-" + index + "-" + i)
      if(selector.length > 0) {
        if(i <= fuel_level) {
          selector.removeClass('empty')
        } else {
          selector.addClass('empty')
        }
      }
    }
  });
});