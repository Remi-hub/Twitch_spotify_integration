let twitchCode;
let twitchId;
let twitchSecret;
let channelName;
let twitchAccessToken;
let twitchRefreshToken;
let broadcasterId;


console.log("hello im at the top of the js script")


// setting up the required scopes
const twitchScopes = "channel:manage:redemptions channel:read:redemptions user:read:email"

// step 1
function sendForm() {
    let twitchId = document.getElementById("twitch-id").value;
    window.location = `https://id.twitch.tv/oauth2/authorize?client_id=${twitchId}&redirect_uri=http://localhost:8080/callbacktwitch&response_type=code&scope=${twitchScopes}`;
}

// step 2 DOES NOT WORK YET
function getTwitchCode() {
    let getTwitchCode = window.location.search;
    getTwitchCode = getTwitchCode.slice(6, 36)
    console.log(`TwitchCode sliced: ${getTwitchCode}`)
    return getTwitchCode
}
// get the response from getTwitchAccessAndRefreshToken and parses it
function storeInformations(response){
    let responseJSON = JSON.parse(response)
    console.log("JE SUIS DANS STORE INFO LA")
    console.log(responseJSON["access_token"])
    twitchRefreshToken = responseJSON["refresh_token"]
    // todo recup le refresh token
    console.log(responseJSON["refresh_token"])
    twitchAccessToken = responseJSON["access_token"]
    console.log(twitchAccessToken)
}

// is being called in the submit function from html 2 to get tokens
async function getTwitchAccessAndRefreshToken(clientId, clientSecret, clientCode){
    var myHeaders = new Headers();

    var requestOptions = {
        method: 'POST',
        headers: myHeaders,
        redirect: 'follow'
    };

    return fetch(`https://id.twitch.tv/oauth2/token?client_id=${clientId}&client_secret=${clientSecret}&code=${clientCode}&grant_type=authorization_code&redirect_uri=http://localhost:8080/callbacktwitch`, requestOptions)
        .then(response => response.text())
        .then(result => storeInformations(result))
        .catch(error => console.log('error', error));
}

// get the user id from the user
async function getUserId() {
    console.log("JE SUIS DANS GET USER ID")
    var myHeaders = new Headers();
    myHeaders.append("Client-Id", twitchId);
    myHeaders.append("Authorization", `Bearer ${twitchAccessToken}`);

    var requestOptions = {
        method: 'GET',
        headers: myHeaders,
        redirect: 'follow'
    };
    return fetch(`https://api.twitch.tv/helix/users?login=${channelName}`, requestOptions)
        .then(response => response.text())
        .then(function (result){
            let resultJon = JSON.parse(result);
            broadcasterId = resultJon["data"][0]["id"]}
        )
        .catch(error => console.log('error', error));
}

// create a custom reward and return its ID
async function createCustomReward(clientId, clientToken, rewardTitle, RewardCost, inputRequired) {
    console.log("JE SUIS DANS CREATE CUSTOM REWARD")
    var myHeaders = new Headers();
    myHeaders.append("Client-Id", twitchId);
    myHeaders.append("Authorization", `Bearer ${twitchAccessToken}`);
    console.log("LE TOKEN EST LA")
    console.log(twitchAccessToken)
    myHeaders.append("Content-Type", "application/x-www-form-urlencoded");

    var urlencoded = new URLSearchParams();
    urlencoded.append("title", rewardTitle);
    urlencoded.append("cost", RewardCost);
    urlencoded.append("is_user_input_required", inputRequired);

    var requestOptions = {
        method: 'POST',
        headers: myHeaders,
        body: urlencoded,
        redirect: 'follow'
    };

    return fetch(`https://api.twitch.tv/helix/channel_points/custom_rewards?broadcaster_id=${broadcasterId}`, requestOptions)
        .then(response => response.text())
        .then(function (result){
            resultJson = JSON.parse(result)
            console.log(result)
            return resultJson["data"][0]["id"]
        })
        .catch(error => console.log('error', error));
}

// get the id, secret and code in the step 2 html
async function submit() {

    twitchCode = getTwitchCode()
    twitchId = document.getElementById("twitch-id").value;
    twitchSecret = document.getElementById("twitch-secret").value;
    channelName = document.getElementById("channel-name").value;
    await getTwitchAccessAndRefreshToken(twitchId, twitchSecret, twitchCode).then(function (){
        getUserId().then(function (){
            createCustomReward(twitchId, twitchAccessToken, "Request Song", "100", true)
                .then(function(rewardId) {
                    storeInformationsInFile(rewardId, "Request_Song")
                })
            createCustomReward(twitchId, twitchAccessToken, "Skip current song", "50", false)
                .then(function(rewardId) {
                    storeInformationsInFile(rewardId, "Skip_current_song")
                })
                .then(function (){
                    storeInformationsInFile(twitchAccessToken, "twitch_access_token")
                })
                .then(function (){
                    storeInformationsInFile(twitchId, "twitch_id")
                })
                .then(function (){
                    storeInformationsInFile(twitchSecret, "twitch_secret")
                })
                .then(function (){
                    storeInformationsInFile(twitchRefreshToken, "twitch_refresh_token")
                })
                .then(function (){
                    storeInformationsInFile(twitchScopes, "twitch_scopes")
                })
                .then(function (){
                    storeInformationsInFile(broadcasterId, "broadcaster_id")
                })
            // todo redirect sur une page daccueil
            // .then(function () {
            //     window.location = "http://localhost:8080/"
            // })
        })
    })
}


function storeInformationsInFile(information, filename){
    let myHeaders = new Headers();
    myHeaders.append("rewardId", information);
    myHeaders.append("rewardType", filename);
    let requestOptions = {
        method: 'GET',
        headers: myHeaders,
        redirect: 'follow'
    }
    fetch("http://localhost:8080/store_informations_twitch", requestOptions)
        .then(response => response.text())
        .then(result => console.log(result))
        .catch(error => console.log('error', error));
}
