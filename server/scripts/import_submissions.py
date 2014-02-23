import os
import ConfigParser

from trello import TrelloClient
from pymongo import MongoClient


def import_submissions():
    cards = get_trello_cards()

    submissions = []
    for index, card in enumerate(cards):
        try:
            submission = get_submission_from_card(card)
            submissions.append(submission.__dict__)
        except MissingBandcampException:
            pass

    insert_submissions_into_db(submissions)


def get_trello_cards():
    """
    Makes an API call to Trello to get all of the cards from Weird Canada's
    New Canadiana board. Requires an OAuth key.
    :return: list of trello cards
    """
    trello_client = TrelloClient(
        api_key=os.environ.get('TRELLO_API_KEY'),
        api_secret=os.environ.get('TRELLO_API_SECRET'),
        token=os.environ.get('TRELLO_OAUTH_KEY'),
        token_secret=os.environ.get('TRELLO_OAUTH_SECRET')
    )

    new_canadiana_board_id = os.environ.get('BOARD_ID')
    new_canadiana_board = trello_client.get_board(new_canadiana_board_id)

    return new_canadiana_board.open_cards()


def get_submission_from_card(card):
    """
    Converts a Trello card into a Weird Canada Submission.

    :param card:
    :return: Submission
    """
    description = getattr(card, 'description', None)
    bandcamp_uri = extract_bandcamp_url(description)

    if not bandcamp_uri:
        raise MissingBandcampException()

    submission = Submission(
        date_submitted=card.create_date,  # An API call...
        bandcamp_uri=bandcamp_uri,
        card_title=card.name,
        trello_uri=card.url,
        is_assigned=len(card.idMembers) == 0
    )

    return submission


def extract_bandcamp_url(description):
    """
    Returns a bandcamp url if there is a string that looks like it might be one.
    If nothing is found, return None
    :param description: a string
    :return: string or None
    """
    for word in description.split(' '):
        if 'bandcamp.com' in word:
            return word

    return None


def insert_submissions_into_db(submissions):
    """
    Clears database and re-adds all Weird Canada submissions.

    :param submissions: a list of Weird Canada submissions
    """
    mongo_host = os.environ.get('MONGO_HOST')
    mongo_port = os.environ.get('MONGO_PORT')
    mongo_client = MongoClient(mongo_host, mongo_port)

    db = mongo_client.wyrd_bandcamp
    inserted_submissions = db.submissions.insert(submissions)

    print 'total number of submissions: ', len(submissions)
    print 'total number of inserted submissions: ', len(inserted_submissions)


class Submission(object):
    """
    A Weird Canada artist submission
    """

    date_submitted = None
    bandcamp_uri = None
    card_title = None
    trello_uri = None
    is_assigned = False

    def __init__(self, *args, **kwargs):
        for attribute, value in kwargs.iteritems():
            setattr(self, attribute, value)

    def __repr__(self):
        return self.card_title


class MissingBandcampException(Exception):
    pass


def set_environment_variables():
    config = ConfigParser.ConfigParser()
    config.read('../config.ini')

    # Trello Settings
    os.environ['TRELLO_API_KEY'] = config.get('trello', 'api_key')
    os.environ['TRELLO_API_SECRET'] = config.get('trello', 'api_secret')
    os.environ['TRELLO_OAUTH_KEY'] = config.get('trello', 'oauth_token_key')
    os.environ['TRELLO_OAUTH_SECRET'] = config.get('trello', 'oauth_token_secret')
    os.environ['BOARD_ID'] = '5229507ee1b4973453001127'

    # Mongo Settings
    os.environ['MONGO_USER'] = config.get('mongo', 'user')
    os.environ['MONGO_PASSWORD'] = config.get('mongo', 'password')
    os.environ['MONGO_HOST'] = config.get('mongo', 'host')
    os.environ['MONGO_PORT'] = config.get('mongo', 'port')


if __name__ == '__main__':
    set_environment_variables()
    import_submissions()
