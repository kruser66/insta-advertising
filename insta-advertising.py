import os
import re
from instagrapi import Client
import instagrapi.exceptions
from dotenv import load_dotenv
from pprint import pprint


def is_user_exist(client, user) -> None:
    try:
        client.user_id_from_username(user)
        return True

    except Exception:
        pass


def check_comments_users(client, post_link):
    regex = '(?:@)([A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?)'

    comments = client.media_comments(
        client.media_pk_from_url(post_link), amount=0
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


def collect_likers(client, post_link):
    likers_users = client.media_likers(
        client.media_pk_from_url(post_link)
    )

    return [user.pk for user in likers_users]


if __name__ == '__main__':

    load_dotenv()
    login = os.getenv('INSTAGRAM_LOGIN')
    password = os.getenv('INSTAGRAM_PASSWORD')

    client = Client()
    client.login(login, password)

    post_link = 'https://www.instagram.com/p/BtON034lPhu/'

    correct_comment_users = check_comments_users(client, post_link)

    id_likers_users = collect_likers(client, post_link)

    like_and_comment_users = [
        x for x in correct_comment_users if x[0] in id_likers_users
    ]
    pprint(like_and_comment_users)
