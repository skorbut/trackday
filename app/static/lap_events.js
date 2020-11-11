var socket = io.connect(
    location.protocol + '//' + document.domain + ':' + location.port + '/lap_events',
    {
        upgrade: false,
        transports: ['websocket']
    }
);

socket.on(
    'connect',
    function() {
        socket.emit('race_events', {data: 'I\'m connected!'});
    }
);


socket.on(
    'lap_finished',
    function(msg) {
        console.log("A lap was finished: " + msg);
        var lap_data = JSON.parse(msg);
        var controller = lap_data["controller"]
        $("#lap-number-" + controller).text(lap_data["lap_number"])
        $("#lap-time-" + controller).html(Math.floor(lap_data["lap_time"] / 1000) + "<small>s</small>" + (lap_data["lap_time"] % 1000) + "<small>ms</small>")
        $("#best-time-" + controller).html(Math.floor(lap_data["best_time"] / 1000) + "<small>s</small>" + (lap_data["best_time"] % 1000) + "<small>ms</small>")
    }
);
