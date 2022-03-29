import re
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob
from datetime import datetime, timedelta
import pytz
  
class SentimentAgent(object):
    
    def __init__(self):
        # keys and tokens from the Twitter Dev Console
        consumer_key = 'ggOuWzjZE9Xie28bJ5t0nivRb'
        consumer_secret = 'WC5oidDnZCx7pN7TSurkx8pE6dYAEJNNdYjWdzE6RjEqxdYcPS'
        access_token = '3998638600-VjShWes81OzpjdSeh1bH3XlZOqR21BZt7dP4rAi'
        access_token_secret = 'Ns395vpXsHb99zvvGyGC1jTKx4IBEGniQzI83Qqvf3YML'
  
        # attempt authentication
        try:
            # create OAuthHandler object
            self.auth = OAuthHandler(consumer_key, consumer_secret)
            # set access token and secret
            self.auth.set_access_token(access_token, access_token_secret)
            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)

            print('logged in')
        except:
            print("Error: Authentication Failed")
  
      # Cleaning the tweets
    def clean_up_tweet(self, txt):
         # Remove mentions, hashtags, retweets and urls
         txt = re.sub(r'@[A-Za-z0-9_]+', '', txt)
         txt = re.sub(r'#', '', txt)
         txt = re.sub(r'RT : ', '', txt)
         txt = re.sub(r'https?:\/\/[A-Za-z0-9\.\/]+', '', txt)
         return txt
  
    def get_tweet_sentiment(self, tweet):

        # create TextBlob object of passed tweet text
        analysis = TextBlob(self.clean_up_tweet(tweet))
        # set sentiment
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'
  
    def get_tweets(self, query, count, hoursAgo, minutesAgo, secondsAgo):

        # empty list to store parsed tweets
        tweets = []
        
        try:
            # call twitter api to fetch tweets
            #fetched_tweets = self.api.search_tweets(q = query, count = count, lang = "en", since_id = date_since)
            fetched_tweets = tweepy.Cursor(self.api.search_tweets,q = query, lang = "en").items(count)
  
            # parsing tweets one by one
            for tweet in fetched_tweets:
                
                # getting the appropiate timeframe for tweets
                timeframe = datetime.now()- timedelta(hours = hoursAgo, minutes = minutesAgo, seconds = secondsAgo)
                
                createdAt = tweet.created_at             

                #only accept tweets that are tweeted after the timeframe
                if(timeframe.replace(tzinfo=pytz.utc) < createdAt.replace(tzinfo=pytz.utc)):

                    # empty dictionary to store required params of a tweet
                    parsed_tweet = {}
                    # saving text of tweet
                    parsed_tweet['text'] = tweet.text
                    # saving sentiment of tweet
                    parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)


                    # appending parsed tweet to tweets list
                    if tweet.retweet_count > 0:
                        # if tweet has retweets, ensure that it is appended only once
                        if parsed_tweet not in tweets:
                            tweets.append(parsed_tweet)
                    else:
                        tweets.append(parsed_tweet)
  
            # return parsed tweets
            return tweets
  
        except tweepy.errors.TweepyException as e:
            # print error (if any)
            print("Error : " + str(e))
  
def main():
    query = 'Donald Trump'
    numberOfTweets = 5
    hoursAgo = 10
    minutesAgo = 10
    secondsAgo = 10

    api = SentimentAgent()
    # calling function to get tweets
    tweets = api.get_tweets(query, numberOfTweets, hoursAgo, minutesAgo, secondsAgo)

    if (len(tweets) !=  0):
        # amount of positive tweets
        ptweets = len([tweet for tweet in tweets if tweet['sentiment'] == 'positive'])      
        print("Positive tweets amount: " , ptweets)

        # amount of negative tweets
        ntweets = len([tweet for tweet in tweets if tweet['sentiment'] == 'negative'])      
        print("Negative tweets amount: " , ntweets)

        # amount of neutral tweets
        #print("Neutral tweets amount:", (len(tweets) -(len( ntweets )+len( ptweets)))/len(tweets))

        if (ptweets > ntweets):
            #positive signal
            print("placeholder positive signal")
        elif(ptweets < ntweets):
            #negative signal
            print("placeholder negative signal")
        else:
            #neutral signal
            print("placeholder no signal")
            

    else:
        #neutral signal
        print("placeholder no signal")
  
if __name__ == "__main__":
    # calling main function
    main()