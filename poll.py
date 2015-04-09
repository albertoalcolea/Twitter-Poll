from datetime import datetime

import Queue

import json

import logging

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

from storage import Storage, DuplicateTweet, DuplicateAuthor
from utils import utc_to_local


logger = logging.getLogger('poll')


class StreamQueueListener(StreamListener):
    def __init__(self, queue, *args, **kwargs):
        self.queue = queue
        super(StreamQueueListener, self).__init__(*args, **kwargs)

    def on_data(self, raw_data):
        logger.debug('Received data')
        data = json.loads(raw_data)
        if 'in_reply_to_status_id' in data:
            self.queue.put(data)
        else:
            logger.error("Unknown message type: " + str(raw_data))

    def on_error(self, status_code):
        logger.error('Error on StreamListener: %s', status_code)

    def on_timeout(self):
        logger.error('Timeout error received')


class InvalidVote(Exception): pass


class Poll(object):
    QUEUE_TIMEOUT = 1000

    def __init__(self, storage, stream, queue, metadata):
        self.storage = storage
        self.stream = stream
        self.queue = queue
        self.metadata = metadata
        self.project_hashtag = self.metadata['project_hashtag'].lower()
        self.set_options = set([h.lower() for h in self.metadata['options']])

    def validate_vote(self, data):
        """
        Checks the tweet contents, at least, two hashtags: the project's hashtag and a unique
        valid vote and checks the correct date of the tweet.
        """
        # Date
        data['published_on'] = utc_to_local(datetime.strptime(data['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))
        if data['published_on'] < self.metadata['start_date'] or \
            data['published_on'] > self.metadata['end_date']:
            self.logger.debug('Invalid published_on: %s', data['published_on'])
            raise InvalidVote()
        # Hashtags
        set_hashtags = set([h['text'].lower() for h in data['entities']['hashtags']])
        if not self.project_hashtag in set_hashtags:
            self.logger.debug('project_hashtag not in hashtags')
            raise InvalidVote()
        vote = self.set_options.intersection(set_hashtags)
        if len(vote) != 1:
            self.logger.debug('Invalid hashtags: %s', vote)
            raise InvalidVote()
        else:
            return vote.pop()

    def register_vote(self, data, vote):
        try:
            tweet = {
                'id': data['id'],
                'author_id': data['user']['id'],
                'author_name': data['user']['screen_name'].encode('utf-8'),
                'published_on': data['published_on'], # Prepared field on validate_vote
                'tweet': data['text'].encode('utf-8'),
                'option': vote,
            }
            if 'retweeted_status' in data and data['retweeted_status'] is not None:
                tweet['is_retweet'] = True
                tweet['original_id'] = data['retweeted_status']['id']
            else:
                tweet['is_retweet'] = False
                tweet['original_id'] = None
        except KeyError as e:
            logger.error('Invalid tweet', exc_info=True)
        else:
            try:
                self.storage.insert_tweet(tweet)
            except DuplicateTweet:
                logger.info('Received an invalid duplicate tweet\n%s', tweet)
            except DuplicateAuthor:
                logger.info('Received an invalid second vote for an user\n%s', tweet)
            else:
                logger.debug('Registered a valid vote')

    def get_data(self):
        while datetime.now() < self.metadata['end_date']:
            try:
                # Timeout to avoid KeyboardInterrupt
                data = self.queue.get(timeout=self.QUEUE_TIMEOUT)
            except Queue.Empty:
                continue
            else:
                yield data

    def run(self):
        for data in self.get_data():
            try:
                vote = self.validate_vote(data)
            except InvalidVote:
                logger.debug('Invalid vote\n%s', data)
                continue
            self.register_vote(data, vote)
        logger.info('Reached the end date')
        self.stream.disconnect()


def main():
    queue = Queue.Queue()

    storage = Storage()
    metadata = storage.get_metadata()
    hashtags = metadata['options'] + [metadata['project_hashtag']]

    auth = OAuthHandler(metadata['consumer_key'], metadata['consumer_secret'])
    auth.set_access_token(metadata['access_token_key'], metadata['access_token_secret'])
    listener = StreamQueueListener(queue)
    stream = Stream(auth, listener)

    poll = Poll(storage, stream, queue, metadata)
    try:
        logger.info('Started the collector')
        stream.filter(track=hashtags, async=True)
        poll.run()
    except (SystemExit, KeyboardInterrupt):
        stream.disconnect()
        logger.info('Interrupted')
    except:
        stream.disconnect()
        logger.critical('Unexpected error', exc_info=True)
    finally:
        if hasattr(stream, '_thread'):
            stream._thread.join()
        logger.info('Exiting...')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Twitter Poll')
    parser.add_argument('-v', '--verbose', help='Verbose mode in log', action='store_true')
    args = parser.parse_args()

    # Set the logger level if -v
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    main()
