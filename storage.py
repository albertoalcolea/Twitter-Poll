import MySQLdb

from contextlib import contextmanager


####################################
# Aux functions
####################################

def connect(user, passwd, db='', host='localhost', port=3306):
    """
    Helper connect method with default params.
    """
    return MySQLdb.connect(
        host=host,
        port=port,
        db=db,
        user=user,
        passwd=passwd,
    )


@contextmanager
def get_cursor_and_commit(connection):
    """
    Aux method to use a cursor with a context manager and commit when the cursor is closed.
    """
    cursor = connection.cursor()
    yield cursor
    connection.commit()
    cursor.close()


def reconect_if_timeout(connection):
    """
    MySQL does not support long live connections (max. timeout: 28800 s = 8 h).
    This auxiliar function checks if the connection 'connection' has ended and reconect if the
    server close the previous connection.
    """
    connection.ping(True)



####################################
# DB API
####################################

class StorageError(Exception): pass
class DuplicateTweet(StorageError): pass
class DuplicateAuthor(StorageError): pass


class Storage(object):
    """
    DB Storage API
    """
    def __init__(self):
        self.connection = connect(user='mysql_user', passwd='mysql_pass', db='twitter_poll')

    def insert_tweet(self, tweet):
        reconect_if_timeout(self.connection)
        with get_cursor_and_commit(self.connection) as cursor:
            try:
                cursor.execute("""
                    INSERT INTO tweets
                    (id, author_id, author_name, published_on, tweet, option, is_retweet, original_id)
                    VALUES (%(id)s, %(author_id)s, %(author_name)s, %(published_on)s, %(tweet)s,
                        %(option)s, %(is_retweet)s, %(original_id)s)
                """, tweet)
            except MySQLdb.IntegrityError as e:
                if e.args[0] == 1062: # Duplicate entry for PRIMARY KEY or UNIQUE constraint
                    if 'PRIMARY' in e.args[1]:
                        raise DuplicateTweet()
                    elif 'UC_author_id' in e.args[1]:
                        raise DuplicateAuthor()
                raise

    def insert_metadata(self, metadata):
        reconect_if_timeout(self.connection)
        with get_cursor_and_commit(self.connection) as cursor:
            cursor.execute("""
                INSERT INTO metadata
                (project_hashtag, start_date, end_date, consumer_key, consumer_secret,
                    access_token_key, access_token_secret)
                VALUES (%(project_hashtag)s, %(start_date)s, %(end_date)s, %(consumer_key)s,
                    %(consumer_secret)s, %(access_token_key)s, %(access_token_secret)s)
            """, metadata)
            db_input = [(r,) for r in metadata['options']]
            cursor.executemany("INSERT INTO options (hashtag) VALUES (%s)", db_input)

    def get_metadata(self):
        reconect_if_timeout(self.connection)
        with get_cursor_and_commit(self.connection) as cursor:
            cursor.execute("""
                SELECT
                    project_hashtag, start_date, end_date, consumer_key, consumer_secret,
                        access_token_key, access_token_secret
                FROM
                    metadata
            """)
            db_res = cursor.fetchone()
            metadata = {
                'project_hashtag': db_res[0],
                'start_date': db_res[1],
                'end_date': db_res[2],
                'consumer_key': db_res[3],
                'consumer_secret': db_res[4],
                'access_token_key': db_res[5],
                'access_token_secret': db_res[6],
            }
            cursor.execute("SELECT hashtag FROM options")
            metadata['options'] = [r[0] for r in cursor.fetchall()]
            return metadata

    def get_results(self):
        reconect_if_timeout(self.connection)
        with get_cursor_and_commit(self.connection) as cursor:
            """
            Get the name from the table options instead the option field from the table tweets
            to preserve the correct case of the hashtag.
            The option field from the table of tweets is stored in lower case.
            """
            cursor.execute("""
                SELECT
                    hashtag, total
                FROM
                    (SELECT
                        option, count(option) AS total
                    FROM
                        tweets
                    GROUP by
                        option
                    ORDER BY
                        total DESC
                    ) AS a
                JOIN
                    options
                ON a.option = options.hashtag
            """)
            return cursor.fetchall()
