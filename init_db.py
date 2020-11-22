import datetime
import json
import random
import string

import peewee
from werkzeug.security import check_password_hash, generate_password_hash

from project import models as db


def rand_str(length):
    return ''.join(random.choice(string.ascii_letters) for i in range(length))


def rand_game():
    return {
        'name': rand_str(12),
        'release_date': datetime.datetime.today(),
        'price': random.randint(20, 500),
        'type': random.choice(('ACT', 'RPG')),
        'platform': random.choice(('NS', 'PS', 'XBOX')),
        'hard_copy': random.randint(300, 2000),
        'image': 'https://xxxx',
        'description': rand_str(12) * 30
    }


with db.database:
    db.database.drop_tables(
        [db.Game, db.Customer, db.Supplier, db.Supply, db.Order, db.OrderStatus, db.OrderContains, db.Transaction, db.Account])
    db.database.create_tables(
        [db.Game, db.Customer, db.Supplier, db.Supply, db.Order, db.OrderStatus, db.OrderContains, db.Transaction, db.Account])

db.Game.delete().execute()

# for i in range(100):
#     db.Game.create(**rand_game())

with open('good_games_target.json', 'r', encoding='utf8') as f:
    duplicate = set()
    games = json.load(f)
    random.shuffle(games)
    for game in games:
        date = datetime.datetime.today() - datetime.timedelta(days=300)
        obj = {
            'name': game['name'],
            'release_date': date,
            'price': game['price'],
            'type': random.choice((('action-adventure game', 'space flight simulation game', 'first-person shooter', 'adventure game', 'combat flight simulator'))),
            'platform': game['platform'],
            'hard_copy': random.randint(300, 1000),
            'image': game['image'],
            'description': game['desc'],
            'alternate_images': ';'.join(game['alternate_images'])
        }
        key = (obj['name'], obj['platform'], obj['image'])
        if key in duplicate:
            continue
        duplicate.add(key)
        db.Game.create(**obj)

        if len(duplicate) > 10:
            print("Only add 10 for test!!!!!")
            break


accounts = [
    {'email': 'lei@admin.com', 'name': '',
        'password': generate_password_hash('123', method='sha256'), 'role': 'admin'},
    {'email': 'long@admin.com', 'name': '',
        'password': generate_password_hash('123', method='sha256'), 'role': 'admin'},
    {'email': 'yi@admin.com', 'name': '',
        'password': generate_password_hash('123', method='sha256'), 'role': 'admin'},
]
for i in accounts:
    db.Account.create(**i)
