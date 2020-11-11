var socket = io.connect(
    location.protocol + '//' + document.domain + ':' + location.port + '/race_events',
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
    'race_finished',
    function(race_id) {
        console.log("The race was finished! Redirecting to stop");
        window.location.replace("/races/" + race_id + "/stop")
    }
);
