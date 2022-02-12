let twitchCode;
let twitchId;
let twitchSecret;
let channelName;
let twitchAccessToken;
let twitchRefreshToken;
let broadcasterId;
// setting up the required scopes
const twitchScopes = "channel:manage:redemptions channel:read:redemptions user:read:email"

// step 1
function sendForm() {
    let twitchId = document.getElementById("twitch-id").value;
    window.location = `https://id.twitch.tv/oauth2/authorize?client_id=${twitchId}&redirect_uri=http://localhost:8080/callbacktwitch&response_type=code&scope=${twitchScopes}`;
}

// step 2
function getTwitchCode() {
    let getTwitchCode = window.location.search;
    getTwitchCode = getTwitchCode.slice(6, 36)
    console.log(`TwitchCode sliced: ${getTwitchCode}`)
    return getTwitchCode
}

function storeInformations(response){
    return new Promise(async function(resolve, reject){
        //ICI le code de store informations
        let responseJSON = JSON.parse(response)
        twitchRefreshToken = responseJSON["refresh_token"]
        twitchAccessToken = responseJSON["access_token"]
        resolve("StoreInformations went well");
    })
}


// is being called in the submit function from html 2 to get tokens
async function getTwitchAccessAndRefreshToken(clientId, clientSecret, clientCode){
    return new Promise(async function(resolve, reject){

        let myHeaders = new Headers();
        let requestOptions = {
            method: 'POST',
            headers: myHeaders,
            redirect: 'follow'
        };

        fetch(`https://id.twitch.tv/oauth2/token?client_id=${clientId}&client_secret=${clientSecret}&code=${clientCode}&grant_type=authorization_code&redirect_uri=http://localhost:8080/callbacktwitch`, requestOptions)
            .then(response => response.text())
            .then(async function(result) {
                await storeInformations(result)
                resolve("Twitch Access Token And Refresh went well");
            } )
            .catch(error => console.log('error', error));
    })}

function getUserId () {
    return new Promise(async function(resolve, reject) {

        var myHeaders = new Headers();
        myHeaders.append("Client-Id", twitchId);
        myHeaders.append("Authorization", `Bearer ${twitchAccessToken}`);

        var requestOptions = {
            method: 'GET',
            headers: myHeaders,
            redirect: 'follow'
        };
        fetch(`https://api.twitch.tv/helix/users?login=${channelName}`, requestOptions)
            .then(response => response.text())
            .then(function (result){
                let resultJon = JSON.parse(result);
                broadcasterId = resultJon["data"][0]["id"]
                resolve("Get User Id went well");
            })
            .catch(error => console.log('error', error));
    })
}


// create a custom reward and return its ID
function createCustomReward(rewardTitle, RewardCost, inputRequired) {
    return new Promise(async function (resolve, reject) {
        let myHeaders = new Headers();
        myHeaders.append("Client-Id", twitchId);
        myHeaders.append("Authorization", `Bearer ${twitchAccessToken}`);
        myHeaders.append("Content-Type", "application/x-www-form-urlencoded");

        let urlencoded = new URLSearchParams();
        urlencoded.append("title", rewardTitle);
        urlencoded.append("cost", RewardCost);
        urlencoded.append("is_user_input_required", inputRequired);

        let requestOptions = {
            method: 'POST',
            headers: myHeaders,
            body: urlencoded,
            redirect: 'follow'
        };

        fetch(`https://api.twitch.tv/helix/channel_points/custom_rewards?broadcaster_id=${broadcasterId}`, requestOptions)
            .then(response => response.text())
            .then(function (result) {
                let resultJson = JSON.parse(result)
                resolve(resultJson["data"][0]["id"]);

            })
            .catch(error => console.log('error', error))

    });
}

// get the id, secret and code in the step 2 html
async function submit() {

    twitchCode = getTwitchCode()
    twitchId = document.getElementById("twitch-id").value;
    twitchSecret = document.getElementById("twitch-secret").value;
    channelName = document.getElementById("channel-name").value;
    document.querySelector("#validate-button").disabled = true;

    let accessPromiseToken = getTwitchAccessAndRefreshToken(twitchId,twitchSecret,twitchCode);
    await accessPromiseToken;
    console.log(accessPromiseToken);

    let promiseGetUserId = getUserId();
    await promiseGetUserId;
    console.log(promiseGetUserId);

    let promiseCreateRequestReward = createCustomReward("Request Song", 100, true);
    await promiseCreateRequestReward.then(async function(rewardId){
        let promiseInformationsInFile = storeInformationsInFile(rewardId, "Request_Song")
        await promiseInformationsInFile;
        console.log(promiseInformationsInFile)
    });
    console.log(promiseCreateRequestReward)

    let promiseCreateSkipReward = createCustomReward("Skip Current Song", 50, false);
    await promiseCreateSkipReward.then(async function (rewardId){
        let promiseInformationsInFile = storeInformationsInFile(rewardId, "Skip_current_song")
        await promiseInformationsInFile;
        console.log(promiseInformationsInFile)
    });
    console.log(promiseCreateSkipReward)

    let listToStore = [
        [twitchAccessToken, "twitch_access_token"],
        [twitchId, "twitch_id"],
        [twitchSecret, "twitch_secret"],
        [twitchRefreshToken, "twitch_refresh_token"],
        [twitchScopes, "twitch_scopes"],
        [broadcasterId, "broadcaster_id"]
        ]

    for(let i = 0; i < listToStore.length; i++) {
        let storeInformationPromise = await storeInformationsInFile(listToStore[i][0],listToStore[i][1]);
        console.log(storeInformationPromise);
    }
    window.location = "http://localhost:8080/";
}


function storeInformationsInFile(information, filename){
    return new Promise(async function(resolve, reject){
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
            .then(function(result){
                resolve("Well stored " + information)
            } )
            .catch(error => console.log('error', error));

    });
}