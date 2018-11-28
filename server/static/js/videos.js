// Load the Youtube IFrame Player API code asynchronously.
var tag = document.createElement('script');
var currVideo;

tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

function onPlayerReady(event) {
  event.target.loadPlaylist({'playlist':playlist});
  currVideo = playlist[event.target.getPlaylistIndex()];
  window.setTimeout(syncVideo, 1000);
}

function onPlayerStateChange(event) {
  currVideo = playlist[event.target.getPlaylistIndex()];
  if(event.data == YT.PlayerState.ENDED) {
    event.target.playVideo();
    var btn = document.getElementById('like-btn');
    btn.removeAttribute('disabled'); // Reset like button.
  }
}

// Updates player time every second.
function syncVideo() {
  var payload = player.getCurrentTime();
  socket.emit('syncvideo', {time: payload, room: room});
  window.setTimeout(syncVideo, 1000);
}

// Disable like button to only allow once per video.
$(document).on('click', '#like-btn', function (e) {
  socket.emit('vote', {})
  var btn = $(e.target);
  btn.attr('disabled', 'disabled');
});
