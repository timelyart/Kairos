from pymongo import MongoClient
from urllib import parse
from tools import log


def connect(str_connection):
    try:
        log.debug(parse.quote(str_connection))
        return MongoClient(parse.quote(str_connection), connect=False)
    except Exception as e:
        log.exception(e)
        return False


def get_collection(client, name):
    try:
        return client[name]
    except Exception as e:
        log.exception(e)
        return False


def post(collection, json, many=True):
    """
    :param collection:
    :param json:
    :param many:
    :return:  array of inserted ids
    """
    result = []
    try:
        posts = collection.posts
        if many:
            result = posts.insert_many(json).inserted_id
        else:
            result = [posts.insert_one(json).inserted_id]
    except Exception as e:
        log.exception(e)
    return result


def test(str_connection, collection):
    result = False

    try:
        client = connect(str_connection)
        db = client.get_database(collection)
        log.info(db)
        result = True
    except Exception as e:
        log.exception(e)

    return result

