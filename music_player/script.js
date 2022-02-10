// require('dotenv').config()

let Base64Code;
let SpotifyClientId;
let SpotifyRefreshToken;

function storeInformations(response){
  let informations = {};
  let lines = response.split("\n")
  for (i = 0; i < lines.length; i++){
    let line = lines[i].split(";")
    if (line.length === 2){
      informations[line[0]] = line[1]
    }
  }
  Base64Code = informations['spotify_base_64']
  SpotifyRefreshToken = informations['refresh_token']
  SpotifyClientId = informations['client_id']
}


function retrieveInformation() {
  var requestOptions = {
    method: 'GET',
    redirect: 'follow'
  };

  fetch("http://localhost:8080/spotify_informations.txt", requestOptions)
      .then(response => response.text())
      .then(result => storeInformations(result))
      .catch(error => console.log('error', error));
}

retrieveInformation()


let currentTrack = {
  trackName: "",
  artist: "",
  duration: 0,
  progression: 0,
  urlCover: ""
};

const trackName = document.getElementById("track-name")
const trackArtist = document.getElementById("track-artist")
const trackDuration = document.getElementById("track-duration")
const trackProgression = document.getElementById("track-progression")
const trackCoverUrl = document.getElementById("track-url-cover")



let myHeaders = new Headers();
myHeaders.append("Content-Type", "application/x-www-form-urlencoded");
myHeaders.append("Authorization", "Basic" + Base64Code);

let urlencoded = new URLSearchParams();
urlencoded.append("grant_type", "refresh_token");
urlencoded.append("refresh_token", SpotifyRefreshToken);
urlencoded.append("client_id", SpotifyClientId);

let requestOptions = {
  method: 'POST',
  headers: myHeaders,
  body: urlencoded,
  redirect: 'follow'
};

let myHeadersForCurrentTrack = new Headers();
myHeadersForCurrentTrack.append("Access-Control-Allow-Origin", "*")



async function getAccessToken() {
  // console.log("calling")
  await fetch("https://accounts.spotify.com/api/token", requestOptions)

      .then(response => response.json())
      .then(data => bearerToken = data["access_token"])
      .catch(error => console.log('error', error));
  console.log(bearerToken)

}


let requestOptionsForCurrentTrack = {
  method: 'GET',
  headers: myHeadersForCurrentTrack,
  redirect: 'follow',
};
let bearerToken;


async function getCurrentlyPlayingTrackFromPython(){
  let myHeadersForCurrentTrack = new Headers();
  myHeadersForCurrentTrack.append("token", bearerToken)
  console.log("LE BEARER TOKEN CEST CA :")
  console.log(bearerToken)
  let requestOptionsForCurrentTrack = {
    method: 'GET',
    headers: myHeadersForCurrentTrack,
    redirect: 'follow',
  };
  await fetch("http://localhost:8080/currently_playing", requestOptionsForCurrentTrack, )
      .then(response =>
          response.json()
      )
      .then(result => {console.log(result);currentTrack = {...currentTrack,
        trackName: result["item"]["name"],
        artist: result["item"]["artists"][0]["name"].slice(0, 30),
        duration: Math.round(result["item"]["duration_ms"] / 1000),
        progression: Math.round(result["progress_ms"] / 1000),
        urlCover: result["item"]["album"]["images"][0]["url"]}} )
      .catch(error => console.log('error', error));
}

function displayInformation(){
  trackName.innerText = currentTrack.trackName
  if ((currentTrack.trackName.length) > 30) {
    trackName.innerText = currentTrack.trackName.slice(0, 30) + "..."}
  trackArtist.innerText = currentTrack.artist
  trackCoverUrl.src = currentTrack.urlCover
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

getAccessToken()

setInterval(function () {
      getAccessToken()
    },
    50*60*1000);



var i = 0;
function move() {
  if (i === 0) {
    i = 1;
    var progressBarInHtml = document.getElementById("bar");
    // le debut de la largeur de la barre
    var progressBarInPercent = currentTrack.progression / currentTrack.duration * 100;
    var id = setInterval(frame, 6000);
    function frame() {
      progressBarInPercent = currentTrack.progression / currentTrack.duration * 100;
      progressBarInHtml.style.width = progressBarInPercent + "%";
    }
  }
}
move()

async function mainLoop() {
  // Sleep in loop
  while ("a" === "a") {
    // await getCurrentlyPlaying()
    await getCurrentlyPlayingTrackFromPython()
    displayInformation()
    await sleep(6000);
  }

}

setTimeout(function (){
  mainLoop()
}, 3000);