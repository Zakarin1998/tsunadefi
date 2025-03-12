import tweepy
import openai

# TODO : 
# - test and improve api
# - image and post publish and generation
# - improved data retrieval
# 

# Configura le API Keys
TWITTER_API_KEY = "your_twitter_api_key"
TWITTER_API_SECRET = "your_twitter_api_secret"
TWITTER_ACCESS_TOKEN = "your_twitter_access_token"
TWITTER_ACCESS_SECRET = "your_twitter_access_secret"

OPENAI_API_KEY = "your_openai_api_key"

# Configura Tweepy per Twitter API
auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)

# Funzione per trovare tweet su Curve Finance
def search_tweets(query="#CurveFinance OR #DeFi OR Curve", count=10):
    tweets = api.search_tweets(q=query, lang="en", count=count, tweet_mode="extended")
    return tweets

# Funzione AI per generare risposte basate su Curve Finance
def generate_ai_reply(tweet_text):
    prompt = f"Rispondi in modo esperto a questo tweet su Curve Finance: {tweet_text}"
    
    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": "Sei un esperto di DeFi."},
                  {"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

# Funzione per rispondere ai tweet
def reply_to_tweets():
    tweets = search_tweets()
    
    for tweet in tweets:
        reply = generate_ai_reply(tweet.full_text)
        api.update_status(status=f"@{tweet.user.screen_name} {reply}", in_reply_to_status_id=tweet.id)
        print(f"Risposto a {tweet.user.screen_name}: {reply}")

# Avvia il bot
reply_to_tweets()
