import os
import re
from instagrapi import Client
from dotenv import load_dotenv
from pprint import pprint


def is_user_exist(client, user) -> None:
    try:
        client.user_id_from_username(user)
        return True

    except Exception:
        pass


def check_comments_users(client, post):
    regex = '(?:@)([A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?)'

    comments = client.media_comments(
        client.media_pk_from_url(post), amount=0
    )

    comments_text = [
        (comment.user, re.findall(regex, comment.text)) for comment in comments
    ]

    correct_comment_users = []
    for user, marked_users in comments_text:
        for marked_user in marked_users:
            if is_user_exist(client, marked_user):
                correct_comment_users.append((user.pk, user.username))
                continue

    return correct_comment_users


def search_likers(client, post):
    likers_users = client.media_likers(
        client.media_pk_from_url(post)
    )

    return [user.pk for user in likers_users]


def search_followers(client, user):
    followers = client.user_followers(
        client.user_info_by_username(user).pk, amount=0
    ).keys()

    return followers


if __name__ == '__main__':

    load_dotenv()
    login = os.getenv('INSTAGRAM_LOGIN')
    password = os.getenv('INSTAGRAM_PASSWORD')

    client = Client()
    client.login(login, password)

    post = 'https://www.instagram.com/p/CUFFXu5IYIN/'
    post_user = 'goldencalfrevda'

    correct_comment_users = check_comments_users(client, post)

    id_likers = search_likers(client, post)
    ids_followers = search_followers(client, post_user)

    complied_rules_users = set([
        x for x in correct_comment_users
        if x[0] in id_likers and x[0] in ids_followers

    ])

    pprint(complied_rules_users)
