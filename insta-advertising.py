import os
import re
import argparse
from instagrapi import Client
from dotenv import load_dotenv
from pprint import pprint
from random import choice


def is_user_exist(client, user) -> None:
    try:
        client.user_id_from_username(user)
        return True

    except Exception:
        pass


def is_correct_post(client, post):
    try:
        client.media_pk_from_url(post)
        return True
    except Exception:
        return False


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


def createParser():
    parser = argparse.ArgumentParser(
        description='Определяем победителя конкурса в Инстаграмм'
    )
    parser.add_argument('post', nargs='?', help='Ссылка на пост в Инстаграмм')

    return parser


def select_winner(client, post):
    client.login(login, password)

    if not is_correct_post(client, post):
        print('Неверная ссылка на пост')
        exit()

    post_user = client.media_user(client.media_pk_from_url(post)).username

    correct_comment_users = check_comments_users(client, post)

    likers_ids = search_likers(client, post)
    followers_ids = search_followers(client, post_user)

    complied_rules_users = set([
        user[1] for user in correct_comment_users
        if user[0] in likers_ids and user[0] in followers_ids
    ])

    return choice(list(complied_rules_users))


if __name__ == '__main__':

    load_dotenv()
    login = os.getenv('INSTAGRAM_LOGIN')
    password = os.getenv('INSTAGRAM_PASSWORD')

    parser = createParser()
    args = parser.parse_args()
    if not args.post:
        parser.print_help()
        exit()

    client = Client()

    winner = select_winner(client, args.post)

    print(
        'Победитель конкурса: {}'.format(winner)
    )
