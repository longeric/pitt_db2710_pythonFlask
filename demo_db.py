from peewee import *

# your db here
database = MySQLDatabase('infsci', user='zhang', password='123', host='192.168.1.110', port=3306)

class Shop(Model):
    name = CharField(primary_key=True)
    create_at = DateField()

    class Meta:
        database = database

with database:
    database.create_tables([Shop])
