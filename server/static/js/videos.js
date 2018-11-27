// Load the Youtube IFrame Player API code asynchronously.
var tag = document.createElement('script');

tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

function onPlayerReady(event) {
  event.target.playVideo();
  event.target.loadPlaylist({'playlist':playlist.slice(1)});
}

function onPlayerStateChange(event) {
  if(event.data == YT.PlayerState.ENDED) {
    event.target.playVideo()
  }
}
