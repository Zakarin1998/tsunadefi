function postTweet() {
    let tweetText = document.getElementById("tweet-text").value;
    if (!tweetText) {
        alert("Please enter a tweet!");
        return;
    }
    fetch('/tweet', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: tweetText })
    })
    .then(response => response.text())
    .then(data => alert(data))
    .catch(error => console.error("Error:", error));
}

function fetchLogs() {
    fetch('/logs')
    .then(response => response.text())
    .then(data => document.getElementById("log-container").innerText = data)
    .catch(error => console.error("Error loading logs:", error));
}

fetchLogs();  // Load logs on page load
