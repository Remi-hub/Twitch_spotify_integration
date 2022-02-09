let SpotifyClientID;
let SpotifyBase64Code;


// setting up the required scopes
const spotifyScopes = "user-read-currently-playing user-modify-playback-state user-read-playback-state"

// step 1
function sendForm() {
    let spotifyId = document.getElementById("spotify-id").value;
    window.location = `https://accounts.spotify.com/authorize?response_type=code&client_id=${spotifyId}&scope=${spotifyScopes}&redirect_uri=http://localhost:8080/callbackspotify`;
}

// step 2
function getSpotifyCode() {
    let spotifyCode = window.location.search;
    spotifyCode = spotifyCode.slice(6, spotifyCode.length)
    return spotifyCode
}
// encode client id and client secret
function encodeBase64(clientId, clientSecret) {
    return btoa(clientId + ":" + clientSecret)
}


// request to get tokens
async function requestAccessAndRefreshTokenSpotify(codeBase64, code){
    let myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/x-www-form-urlencoded");
    myHeaders.append("Authorization", "Basic " + codeBase64);

    let urlencoded = new URLSearchParams();
    urlencoded.append("grant_type", "authorization_code");
    urlencoded.append("code", code);
    urlencoded.append("redirect_uri", "http://localhost:8080/callbackspotify");

    let requestOptions = {
        method: 'POST',
        headers: myHeaders,
        body: urlencoded,
        redirect: 'follow'
    };

    fetch("https://accounts.spotify.com/api/token", requestOptions)
        .then(response => response.text())
        .then(result => storeInformations(result))
        .catch(error => console.log('error', error));
}

function storeInformations(response){
    let responseJson = JSON.parse(response)
    let refreshToken = responseJson["refresh_token"]
    console.log(responseJson)
    let myHeaders = new Headers();
    myHeaders.append("token", refreshToken);
    myHeaders.append("client_id", SpotifyClientID);
    myHeaders.append("Spotify_base_64", SpotifyBase64Code);
    let requestOptions = {
        method: 'GET',
        headers: myHeaders,
        redirect: 'follow'
    };

    fetch("http://localhost:8080/store_informations", requestOptions)
        .then(response => response.text())
        .then(result => window.location = "http://localhost:8080/index.html")
        .catch(error => console.log('error', error));
}

async function submit() {
    let spotifyCode = getSpotifyCode()
    let spotifyId = document.getElementById("spotify-id").value;
    let spotifySecret = document.getElementById("spotify-secret").value;
    let codeBase64 = encodeBase64(spotifyId, spotifySecret);
    SpotifyBase64Code = codeBase64;
    SpotifyClientID = spotifyId;
    await requestAccessAndRefreshTokenSpotify(codeBase64, spotifyCode);
    console.log()

}

