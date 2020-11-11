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
    function(msg) {
        console.log("The race was finished: " + msg);
    }
);
