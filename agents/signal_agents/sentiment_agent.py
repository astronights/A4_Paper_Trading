import re
import time
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob
from .base_signal_agent import BaseSignalAgent
from config import twitter, constants
from datetime import datetime, timedelta, timezone
import logging

import numpy as np
from skfuzzy import control as ctrl, trimf as trimf
  
class SentimentAgent(BaseSignalAgent):
    
    def __init__(self):
        super().__init__()
        self.signals = []
        self.api = None
        # Attempt authentication
        try:
            # Create OAuthHandler object
            self.auth = OAuthHandler(twitter.CONSUMER_KEY, twitter.CONSUMER_SECRET)
            # Set access token and secret
            self.auth.set_access_token(twitter.ACCESS_TOKEN, twitter.ACCESS_TOKEN_SECRET)
            # Create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
        except:
            logging.error("Error: Authentication Failed")

    def run(self):
        while True:
            self.signal()
            time.sleep(constants.TICK)

    def signal(self):
        self.lock.acquire()
        query = 'Bitcoin'
        hoursAgo = secondsAgo = 0
        tweets = self._get_tweets(query, twitter.NUM_TWEETS, hoursAgo, constants.TIMEFRAME, secondsAgo)
        if (len(tweets) >  0):
            sentiment = sum([t['sentiment'] for t in tweets])/len(tweets)
            self.signals.append((1.0 if sentiment > 50.0 else -1.0))
        else:
            self.signals.append(0.0)
        self.updated = True
        logging.info(f'Sentiment Signal: {self.signals[-1]}')
        self.lock.release()


    # Getting the tweets required for the specified timeframe
    def _get_tweets(self, query, count, hoursAgo, minutesAgo, secondsAgo):
        # Empty list to store parsed tweets
        tweets = []
        earliest_time = datetime.now(timezone.utc) - timedelta(hours = hoursAgo, minutes = minutesAgo, seconds = secondsAgo)
        try:
            # Call twitter api to fetch tweets
            fetched_tweets = tweepy.Cursor(self.api.search_tweets,q = query, lang = "en").items(count)
  
            # Parsing tweets one by one
            for tweet in fetched_tweets:
                # Getting the appropiate timeframe for tweets
                
                createdAt = tweet.created_at
                # Only accept tweets that are tweeted after the timeframe
                if(earliest_time < createdAt):

                    # Empty dictionary to store required params of a tweet
                    parsed_tweet = {}
                    # Saving text of tweet
                    parsed_tweet['text'] = tweet.text
                    # Saving sentiment of tweet
                    parsed_tweet['sentiment'] = self._get_tweet_sentiment(tweet.text)

                    tweets.append(parsed_tweet)
  
            # Return parsed tweets
            return tweets
  
        except tweepy.errors.TweepyException as e:
            logging.error("Error : " + str(e))

    # Getting the tweet's polarity and subjectivity with TextBlob
    def _get_tweet_sentiment(self, tweet):
        # Create TextBlob object of passed tweet text
        analysis = TextBlob(self._clean_up_tweet(tweet))
        # Set sentiment
        tweetData = (analysis.sentiment.polarity, analysis.sentiment.subjectivity)
        tweetGrade = self._fuzzy_logic_get_tweet_grade(tweetData)

        return(tweetGrade)
  
    # Cleaning the tweets for sentiment analysis
    def _clean_up_tweet(self, txt):
         # Remove mentions, hashtags, retweets and urls
         txt = re.sub(r'@[A-Za-z0-9_]+', '', txt)
         txt = re.sub(r'#', '', txt)
         txt = re.sub(r'RT : ', '', txt)
         txt = re.sub(r'https?:\/\/[A-Za-z0-9\.\/]+', '', txt)
         return txt

         
    """
    Fuzzy logic is applied using the tweets' polarities and subjectivities.
    Polarity refers to how positive the tweet is, a higher number means its more positive.
    Subjectivity refers to how subjective(based on feelings) the tweet is, a higher number means tis more suibjective.
    The idea behind the fuzzy logic is that subjectivity influence how reliable the tweet's polarity is, therefore,
    a tweet with low subjectivity score is more ideal to generate a signal (both positive and negative),
    while a tweet with high subjectivity score is more prone to be ignored.
    """  
    def _fuzzy_logic_get_tweet_grade(self, tweetData):
        curPolarity = tweetData[0]
        curSubjectivity = tweetData[1]

        polarity = ctrl.Antecedent(np.arange(-1.0, 1.0, 0.1), 'polarity')
        subjectivity = ctrl.Antecedent(np.arange(0.0, 1.0, 0.1), 'subjectivity')
        strength = ctrl.Consequent(np.arange(0, 101, 1), 'strength')

        polarity.automf(3)
        
        subjectivity['good'] = trimf(subjectivity.universe, [0, 0, 0.5])
        subjectivity['average'] = trimf(subjectivity.universe, [0, 0.5, 1])
        subjectivity['poor'] = trimf(subjectivity.universe, [0.5, 1, 1])

        strength['strongly_negative'] = trimf(strength.universe, [0, 0, 25])
        strength['negative'] = trimf(strength.universe, [0, 25, 50])
        strength['neutral'] = trimf(strength.universe, [25, 50, 75])
        strength['positive'] = trimf(strength.universe, [50, 75, 100])
        strength['strongly_positive'] = trimf(strength.universe, [75, 100, 100])

        rule1 = ctrl.Rule(polarity['poor'] & subjectivity['good'], strength['strongly_negative'])
        rule2 = ctrl.Rule(polarity['poor'] & subjectivity['average'], strength['negative'])
        rule3 = ctrl.Rule(polarity['average'] | subjectivity['poor'], strength['neutral'])
        rule4 = ctrl.Rule(polarity['good'] & subjectivity['average'], strength['positive'])
        rule5 = ctrl.Rule(polarity['good'] & subjectivity['good'], strength['strongly_positive'])

        # Assign the rules
        sentiment_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5])
        sentiment = ctrl.ControlSystemSimulation(sentiment_ctrl)

        sentiment.input['polarity'] = curPolarity
        sentiment.input['subjectivity'] = curSubjectivity

        # Crunch the numbers
        sentiment.compute()
        sentimentStrength = sentiment.output['strength']

        return sentimentStrength