import datetime

from storage import Storage


# METADATA = {
#   # Hashtags (without #)
#   'project_hashtag': 'eventName',
#   'options': ['...', '...', '...'],
#   # Start and end
#   'start_date': datetime.datetime(2015, 1, 1, 10, 0),
#   'end_date': datetime.datetime(2015, 1, 2, 10, 0),
#   # Twitter OAUTH keys
#   'consumer_key': '',
#   'consumer_secret': '',
#     'access_token_key': '',
#     'access_token_secret': '',
# }
METADATA = {
    # Hashtags (without #)
    'project_hashtag': 'eventName',
    'options': ['option1', 'option2', 'optionThree'],
    # Start and end
    'start_date': datetime.datetime(2015, 4, 2, 18, 0),
    'end_date': datetime.datetime(2015, 4, 2, 19, 0),
    # Twitter OAUTH keys
    'consumer_key': '',
    'consumer_secret': '',
    'access_token_key': '',
    'access_token_secret': '',
}


storage = Storage()
try:
    storage.insert_metadata(METADATA)
except:
    raise
else:
    print 'DONE!'
