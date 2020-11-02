import datetime
import random
import string
import peewee
from project import models as db


# name = CharField()
#     release_date = DateField()
#     price = DoubleField()
#     type = CharField()
#     platform = CharField()
#     hard_copy = IntegerField()
#     image = CharField(max_length=1024)
#     description = CharField(max_length=2048)

def rand_str(length):
    return ''.join(random.choice(string.ascii_letters) for i in range(length))

def rand_game():
    return {
        'name': rand_str(12),
        'release_date': datetime.datetime.today(),
        'price': random.randint(20,500),
        'type': random.choice(('ACT', 'RPG')),
        'platform': random.choice(('NS', 'PS', 'XBOX')),
        'hard_copy': random.randint(300, 2000),
        'image': 'https://xxxx',
        'description': rand_str(12) * 30
    }


with db.database:
    db.database.drop_tables(
        [db.Game, db.Customer, db.Supplier, db.Supply, db.Order, db.OrderStatus, db.Transaction, db.Account])
    db.database.create_tables(
        [db.Game, db.Customer, db.Supplier, db.Supply, db.Order, db.OrderStatus, db.Transaction, db.Account])

db.Game.delete().execute()
for i in range(100):
    db.Game.create(**rand_game() )

accounts = [
    {'email': 'lei@admin.com', 'name': '', 'password': '123', 'role': 'admin'},
    {'email': 'long@admin.com', 'name': '', 'password': '123', 'role': 'admin'},
    {'email': 'yi@admin.com', 'name': '', 'password': '123', 'role': 'admin'},
]
for i in accounts:
    db.Account.create(**i)
