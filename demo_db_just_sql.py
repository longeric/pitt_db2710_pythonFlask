import mysql.connector
import datetime

cnx = mysql.connector.connect(user='zhang', password='123',
                              host='192.168.1.110',
                              database='infsci')

def create_tables():
    try:
        cursor = cnx.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS `shop` (
            `name` char(56),
            `created_at` date not NULL,
            PRIMARY KEY (`name`)
        )''')
    except mysql.connector.Error as err:
        print("Failed creating tables: {}".format(err))
        # todo: exception

def insert_shop(name):
    add = 'insert into shop (name, created_at) values (%s, %s)';
    data = (name, datetime.date.today())
    try:
        cursor = cnx.cursor()
        cursor.execute(add, data)
    except mysql.connector.Error as err:
        print("Failed insert_shop: {}".format(err))


def get_shop_names():
    try:
        cursor = cnx.cursor()
        cursor.execute('SELECT name from shop')
        out = []
        for (name, ) in cursor:
            out.append(name)
        return out
    except mysql.connector.Error as err:
        print("Failed get_shop_names: {}".format(err))


def get_shop_detail(name):
    try:
        cursor = cnx.cursor()
        cursor.execute('SELECT name, created_at from shop where name = %s', (name, ))
        for (name, created_at) in cursor:
            return name, created_at
    except mysql.connector.Error as err:
        print("Failed get_shop_names: {}".format(err))

create_tables()

if __name__ == '__main__':
    print(get_shop_names())
    insert_shop("first shop")
    print(get_shop_names())
    print(get_shop_detail("first shop"))

cnx.close()
