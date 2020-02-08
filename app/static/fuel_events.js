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
    $("#fuel-gauge-canvas-" + index)[0].setAttribute('data-value', fuel_level);
  });
});