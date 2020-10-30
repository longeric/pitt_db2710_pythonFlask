from peewee import *

# your db here
database = MySQLDatabase('infsci', user='lei',
                         password='123', host='127.0.0.1', port=3306)


class Shop(Model):
    name = CharField(primary_key=True)
    create_at = DateField()

    class Meta:
        database = database

################


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


class Customer(Model):
    phone = CharField(unique=True)
    email = CharField(unique=True)
    first_name = CharField()
    last_name = CharField()

    password = CharField()

    addr_country = CharField()
    addr_state = CharField()
    addr_city = CharField()
    addr_street = CharField()
    addr_zipcode = CharField()

    # todo: default payment info
    # card type
    # card number
    # expire at
    # card holder's name
    # billing addr

    class Meta:
        database = database


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


class Admin(Model):
    name = CharField(unique=True)
    password = CharField()
    role = CharField()

    class Meta:
        database = database


######################

with database:
    database.create_tables(
        [Game, Customer, Supplier, Supply, Order, OrderStatus, Transaction, Admin])
