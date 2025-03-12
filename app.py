import os
from flask import Flask, redirect, request, session, url_for, render_template
from requests_oauthlib import OAuth1Session
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "your-secret-key")

# Twitter OAuth1.0a configuration
CONSUMER_KEY = os.environ.get("TWITTER_API_KEY")
CONSUMER_SECRET = os.environ.get("TWITTER_API_SECRET_KEY")
CALLBACK_URI = os.environ.get("TWITTER_CALLBACK_URI", "http://127.0.0.1:5000/callback")

# OAuth Endpoints
REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
AUTHORIZATION_URL = "https://api.twitter.com/oauth/authorize"
ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    """
    Step 1: Obtain a request token.
    """
    try:
        oauth = OAuth1Session(CONSUMER_KEY,
                              client_secret=CONSUMER_SECRET,
                              callback_uri=CALLBACK_URI)
        # Fetch the request token
        fetch_response = oauth.fetch_request_token(REQUEST_TOKEN_URL)
    except Exception as e:
        return f"Error fetching request token: {e}"

    # Store the token and secret in session for later use
    session['oauth_token'] = fetch_response.get('oauth_token')
    session['oauth_token_secret'] = fetch_response.get('oauth_token_secret')

    # Step 2: Redirect the user to Twitter for authorization
    authorization_url = oauth.authorization_url(AUTHORIZATION_URL)
    return redirect(authorization_url)


@app.route('/callback')
def callback():
    """
    Step 3: Convert the request token into an access token.
    """
    # Retrieve the request token and verifier from the callback URL
    oauth_verifier = request.args.get('oauth_verifier')
    oauth_token = session.get('oauth_token')
    oauth_token_secret = session.get('oauth_token_secret')

    if not oauth_verifier or not oauth_token or not oauth_token_secret:
        return "Missing OAuth verifier or token. Try logging in again.", 400

    # Create a new OAuth1Session with the request token details
    oauth = OAuth1Session(CONSUMER_KEY,
                          client_secret=CONSUMER_SECRET,
                          resource_owner_key=oauth_token,
                          resource_owner_secret=oauth_token_secret,
                          verifier=oauth_verifier)
    try:
        # Fetch the access token
        oauth_tokens = oauth.fetch_access_token(ACCESS_TOKEN_URL)
    except Exception as e:
        return f"Error fetching access token: {e}"

    # Store access tokens in session for further API calls
    session['access_token'] = oauth_tokens.get('oauth_token')
    session['access_token_secret'] = oauth_tokens.get('oauth_token_secret')

    return redirect(url_for('index'))


@app.route('/tweet', methods=['POST'])
def tweet():
    """
    Post a tweet on behalf of the authenticated user.
    """
    access_token = session.get('access_token')
    access_token_secret = session.get('access_token_secret')

    if not access_token or not access_token_secret:
        return "You must be logged in to post a tweet!", 401

    # Get tweet text from the POST JSON data
    data = request.get_json()
    tweet_text = data.get("text", "")
    if not tweet_text:
        return "Tweet text cannot be empty!", 400

    # Create an OAuth1Session using the user access tokens
    oauth = OAuth1Session(CONSUMER_KEY,
                          client_secret=CONSUMER_SECRET,
                          resource_owner_key=access_token,
                          resource_owner_secret=access_token_secret)

    # Post tweet using Twitter API v1.1 endpoint
    response = oauth.post(
        "https://api.twitter.com/1.1/statuses/update.json",
        params={"status": tweet_text}
    )

    if response.status_code == 200:
        return "Tweet posted successfully! 🎉"
    else:
        return f"Error posting tweet: {response.text}", response.status_code


if __name__ == '__main__':
    app.run(debug=True)
