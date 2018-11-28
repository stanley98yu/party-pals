var socket;
$(document).ready(function(){
  socket = io.connect('http://' + document.domain + ':' + location.port + '/party');

  socket.on('connect', function() {
    socket.emit('joined', {});

    socket.once('disconnect', function() {
      socket.emit('left', {});
    });
  });
  
  socket.on('status', function(data) {
    $('#chat').val($('#chat').val() + '<' + data.msg + '>\n');
    $('#chat').scrollTop($('#chat')[0].scrollHeight);
  });

  socket.on('message', function(data) {
    $('#chat').val($('#chat').val() + data.username + ': ' + data.msg + '\n');
    $('#chat').scrollTop($('#chat')[0].scrollHeight);
  });

  socket.on('update-vid', function(data) {
    player.seekTo(data['time']);
  });

  $('#text').keypress(function(e) {
    var code = e.keyCode || e.which;
    if (code == 13) {
        text = $('#text').val();
        $('#text').val(''); // Reset comment field.
        socket.emit('comment', {msg: text});
    }
  });
});

function leave_room() {
    socket.emit('left', {}, function() {
        socket.disconnect();
        // go back to the login page
        window.location.href = "/";
    });
}
