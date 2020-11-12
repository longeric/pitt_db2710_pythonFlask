from flask_login import UserMixin
from peewee import *

# your db here
database = MySQLDatabase('infsci', user='lei',
                         password='123', host='127.0.0.1', port=3306)

class Game(Model):
    name = CharField()
    release_date = DateField()
    price = DoubleField()
    type = CharField()
    platform = CharField()
    hard_copy = IntegerField()
    image = CharField(max_length=1024)
    description = CharField(max_length=2048)

    class Meta:
        database = database


class Account(Model, UserMixin):
    email = CharField(primary_key=True)
    name = CharField()
    password = CharField()
    role = CharField()

    class Meta:
        database = database


class Customer(Model):
    account = ForeignKeyField(Account)
    first_name = CharField(default='')
    last_name = CharField(default='')
    phone = CharField(default='')

    addr_country = CharField(default='')
    addr_state = CharField(default='')
    addr_city = CharField(default='')
    addr_street = CharField(default='')
    addr_zipcode = CharField(default='')

    card_type = CharField(default='')
    card_number = CharField(default='')
    card_expire_at = DateField(default='2020-01-01')
    card_holder_name = CharField(default='')
    billing_addr_country = CharField(default='')
    billing_addr_state = CharField(default='')
    billing_addr_city = CharField(default='')
    billing_addr_street = CharField(default='')
    billing_addr_zipcode = CharField(default='')

    class Meta:
        database = database


# class Cart(Model):
#     customer = ForeignKeyField(Customer)
#     game = ForeignKeyField(Game)
#     number = IntegerField()


class Supplier(Model):
    name = CharField(unique=True)
    email = CharField(unique=True)
    phone = CharField(unique=True)

    addr_country = CharField()
    addr_state = CharField()
    addr_city = CharField()
    addr_street = CharField()
    addr_zipcode = CharField()

    class Meta:
        database = database


class Supply(Model):
    game = ForeignKeyField(Game)
    Supplier = ForeignKeyField(Supplier)
    copies = IntegerField()
    date = DateTimeField()

    class Meta:
        database = database


class Order(Model):
    game = ForeignKeyField(Game)
    customer = ForeignKeyField(Customer)
    datetime = DateTimeField()

    addr_name = CharField()
    addr_country = CharField()
    addr_state = CharField()
    addr_city = CharField()
    addr_street = CharField()
    addr_zipcode = CharField()

    class Meta:
        database = database


class OrderStatus(Model):
    order = ForeignKeyField(Order)
    status = CharField()
    note = CharField(1024)
    datetime = DateTimeField()

    class Meta:
        database = database


class Transaction(Model):
    order = ForeignKeyField(Order)
    type = CharField()  # pay/refund
    amount = IntegerField()
    card_num = CharField()
    card_holder = CharField()
    datetime = DateTimeField()
    note = CharField()

    class Meta:
        database = database


with database:
    database.create_tables(
        [Game, Customer, Supplier, Supply, Order, OrderStatus, Transaction, Account])