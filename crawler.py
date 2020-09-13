import time as t
import pandas as pd
import tweepy
from datetime import datetime, date, time, timedelta

reg = "[^A-Za-z0-9 ]+"

# override tweepy.StreamListener to add logic to on_status
class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        print(status.text)


api_key = ""
api_secret = ""

access_token_key = ""
access_token_secret = ""

def get_fulltext_from_UserTimeline(tweet):

    if hasattr(tweet, 'retweeted_status'):

        return 'RT @'+ tweet.retweeted_status.user.screen_name + ' ' + tweet.retweeted_status.full_text

    elif hasattr(tweet, 'quoted_status'):

        tt = tweet.full_text

        return tt + " Quote @"+tweet.quoted_status.user.screen_name + ' ' + tweet.quoted_status.full_text

    else:

        return tweet.full_text

def get_quoted_or_retweeted_screen_name(status:tweepy.models.Status):

    if hasattr(status, 'retweeted_status'):

        return 'RT @'+ status.retweeted_status.user.screen_name

    elif hasattr(status, 'quoted_status'):

        return "Quote @"+status.quoted_status.user.screen_name

    else:

        return "None"

def get_reply_to_user(status:tweepy.models.Status):
    reply_to_user = status.in_reply_to_screen_name

    if reply_to_user is None:
        return "None"
    else:
        return reply_to_user

def get_reply_to_tweet_id(status:tweepy.models.Status):
    reply_to_tweet_id = status.in_reply_to_status_id_str

    if reply_to_tweet_id is None:
        return "None"
    else:
        return reply_to_tweet_id

def get_official():

    with open("./list.csv", 'r') as textfile:
        line = textfile.readline()
        cnt = 1

        while line:

            if cnt == 1:
                line = textfile.readline()
                cnt += 1
                continue

            line_list = line.split(",")

            index = line_list[0]
            state = line_list[1]
            official = line_list[4]
            personal = line_list[5]
            name = line_list[6]
            print("Line {}: {}-{}-{}-{}".format(cnt, state, official, personal, name))


            user = api.get_user(official, tweet_mode="extended")

            print("name: " + user.name)
            print("screen_name: " + user.screen_name)
            print("description: " + user.description)
            print("statuses_count: " + str(user.statuses_count))
            print("friends_count: " + str(user.friends_count))
            print("followers_count: " + str(user.followers_count))

            tweets = user.statuses_count
            account_created_date = user.created_at
            delta = datetime.utcnow() - account_created_date
            account_age_days = delta.days
            print("Account age (in days): " + str(account_age_days))

            if account_age_days > 0:
                print("Average tweets per day: " + "%.2f" % (float(tweets) / float(account_age_days)))
            print()

            frame = pd.DataFrame()

            ids = []
            texts = []
            createds = []
            retweets = []
            favs = []
            followers = []
            friends = []
            locs = []
            hashtags_list = []
            mentions_list = []
            screen_name_reply_to_list = []
            tweet_reply_to_list = []
            quoted_or_retweeted_screen_name_list = []

            for pages in tweepy.Cursor(api.user_timeline, screen_name=official, count=200,
                                       tweet_mode="extended").pages():

                for status in pages:
                    # tweets_encoded = status.text.encode('utf-8')
                    # tweets_decoded = tweets_encoded.decode('utf-8')
                    hashtags = ", ".join([hashtag_item['text'] for hashtag_item in status.entities['hashtags']])
                    mentions = ", ".join([mention['screen_name'] for mention in status.entities['user_mentions']])

                    reply_to_user = get_reply_to_user(status)
                    reply_to_tweet_id = get_reply_to_tweet_id(status)
                    quoted_or_retweeted_screen_name = get_quoted_or_retweeted_screen_name(status)

                    tweets_encoded = get_fulltext_from_UserTimeline(status)
                    tweets_encoded = tweets_encoded.replace(",", "")
                    tweets_encoded = tweets_encoded.replace(";", " ")

                    ids.append(status.id)
                    texts.append(tweets_encoded)
                    createds.append(status.created_at)
                    retweets.append(status.retweet_count)
                    favs.append(status.favorite_count)
                    followers.append(status.user.followers_count)
                    friends.append(status.user.friends_count)
                    locs.append(status._json["user"]["location"])

                    hashtags_list.append(hashtags)
                    mentions_list.append(mentions)
                    screen_name_reply_to_list.append(reply_to_user)
                    tweet_reply_to_list.append(reply_to_tweet_id)
                    quoted_or_retweeted_screen_name_list.append(quoted_or_retweeted_screen_name)

            frame["tweet_id"] = ids
            frame["text"] = texts
            frame["created_at"] = createds
            frame["retweet_count"] = retweets
            frame["favorite_count"] = favs
            frame["followers_count"] = followers
            frame["friends_count"] = friends
            frame["tweet_id"] = ids
            frame["text"] = texts

            frame["hashtags"] = hashtags_list
            frame["mentions"] = mentions_list
            frame["reply_to_user"] = screen_name_reply_to_list
            frame["reply_to_tweet_id"] = tweet_reply_to_list
            frame["quoted_or_retweeted_screen_name"] = quoted_or_retweeted_screen_name_list

            frame["location"] = locs

            frame.to_csv("./governors_official/" + state + "_official" + ".csv", sep=',', encoding='utf-8')

            line = textfile.readline()
            cnt += 1

            t.sleep(3)

    textfile.close()

def get_personal():

    with open("./list.csv", 'r') as textfile:
        line = textfile.readline()
        cnt = 1

        while line:

            if cnt == 1:
                line = textfile.readline()
                cnt += 1
                continue

            line_list = line.split(",")

            index = line_list[0]
            state = line_list[1]
            official = line_list[4]
            personal = line_list[5]
            name = line_list[6]
            print("Line {}: {}-{}-{}-{}".format(cnt, state, official, personal, name))

            if personal.lower() == "none" or personal.lower() == "protected":
                line = textfile.readline()
                cnt += 1
                continue

            user = api.get_user(personal, tweet_mode="extended")

            print("name: " + user.name)
            print("screen_name: " + user.screen_name)
            print("description: " + user.description)
            print("statuses_count: " + str(user.statuses_count))
            print("friends_count: " + str(user.friends_count))
            print("followers_count: " + str(user.followers_count))

            tweets = user.statuses_count
            account_created_date = user.created_at
            delta = datetime.utcnow() - account_created_date
            account_age_days = delta.days
            print("Account age (in days): " + str(account_age_days))

            if account_age_days > 0:
                print("Average tweets per day: " + "%.2f" % (float(tweets) / float(account_age_days)))
            print()

            frame = pd.DataFrame()

            ids = []
            texts = []
            createds = []
            retweets = []
            favs = []
            followers = []
            friends = []
            locs = []
            hashtags_list = []
            mentions_list = []
            screen_name_reply_to_list = []
            tweet_reply_to_list = []
            quoted_or_retweeted_screen_name_list = []

            for pages in tweepy.Cursor(api.user_timeline, screen_name=personal, count=200,
                                       tweet_mode="extended").pages():

                for status in pages:
                    # tweets_encoded = status.text.encode('utf-8')
                    # tweets_decoded = tweets_encoded.decode('utf-8')
                    hashtags = ", ".join([hashtag_item['text'] for hashtag_item in status.entities['hashtags']])
                    mentions = ", ".join([mention['screen_name'] for mention in status.entities['user_mentions']])

                    reply_to_user = get_reply_to_user(status)
                    reply_to_tweet_id = get_reply_to_tweet_id(status)
                    quoted_or_retweeted_screen_name = get_quoted_or_retweeted_screen_name(status)

                    tweets_encoded = get_fulltext_from_UserTimeline(status)
                    tweets_encoded = tweets_encoded.replace(",", "")
                    tweets_encoded = tweets_encoded.replace(";", " ")

                    ids.append(status.id)
                    texts.append(tweets_encoded)
                    createds.append(status.created_at)
                    retweets.append(status.retweet_count)
                    favs.append(status.favorite_count)
                    followers.append(status.user.followers_count)
                    friends.append(status.user.friends_count)
                    locs.append(status._json["user"]["location"])

                    hashtags_list.append(hashtags)
                    mentions_list.append(mentions)
                    screen_name_reply_to_list.append(reply_to_user)
                    tweet_reply_to_list.append(reply_to_tweet_id)
                    quoted_or_retweeted_screen_name_list.append(quoted_or_retweeted_screen_name)

            frame["tweet_id"] = ids
            frame["text"] = texts
            frame["created_at"] = createds
            frame["retweet_count"] = retweets
            frame["favorite_count"] = favs
            frame["followers_count"] = followers
            frame["friends_count"] = friends
            frame["tweet_id"] = ids
            frame["text"] = texts

            frame["hashtags"] = hashtags_list
            frame["mentions"] = mentions_list
            frame["reply_to_user"] = screen_name_reply_to_list
            frame["reply_to_tweet_id"] = tweet_reply_to_list
            frame["quoted_or_retweeted_screen_name"] = quoted_or_retweeted_screen_name_list

            frame["location"] = locs

            frame.to_csv("./governors_personal/" + state + "_personal" + ".csv", sep=',', encoding='utf-8')

            line = textfile.readline()
            cnt += 1

            t.sleep(3)

    textfile.close()


if __name__ == "__main__":
    # Authenticate to Twitter
    auth = tweepy.OAuthHandler(api_key, api_secret)
    auth.set_access_token(access_token_key, access_token_secret)

    # Create API object
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    pointer = 36
    # Create a tweet
    try:
        api.verify_credentials()
        print("Authentication OK")
    except:
        print("Error during authentication")

    # target = "realDonaldTrump"


    condition = "personal"

    if condition == "personal":
        get_personal()

    elif condition == "official":
        get_official()


