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
  }
}

// Updates player time every second.
function syncVideo() {
  var payload = player.getCurrentTime();
  socket.emit('syncvideo', {time: payload, room: room});
  window.setTimeout(syncVideo, 1000);
}
