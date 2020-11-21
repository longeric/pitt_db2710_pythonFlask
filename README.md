# Pitt DB project

Demo has been moved to `demo` branch

## Requires

- Python3

## How to install

```
pip install -r requirements.txt
```

## MySQL

- modify `project/models.py` to connect to your database.
- run `init_db.py` to fill databse.

## How to run

### Win
```
set FLASK_APP=project
set FLASK_ENV=development
flask run
```

### Linux
```
export FLASK_APP=project
flask run
```

### Then visit [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in browser

## More examples
- [here](https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login)
- [here](https://github.com/coleifer/peewee/tree/master/examples/twitter)

## APIs
- [Flask](https://flask.palletsprojects.com/en/1.1.x/quickstart/)
- [peewee](http://docs.peewee-orm.com/en/latest/peewee/quickstart.html)

## TODO:
- admin: game remove x
- show name/hello on headers
- home (shop list)
    - image size!
    - order by (default by platform)
    - add to cart; show cart numbers
    - search bar (frontend? backend?)
- cart / checkout
    - add/remove/clear
    - checkout
    - fill address
    - payments
- profile: my orders (history)
    - order list
    - order status / track
    - ? comments ?
    - reset password

## test(qsl):
   -customer
    UPDATE `infsci`.`customer` SET `first_name` = 'y', `last_name` = 't', `phone` = '412888888', `addr_country` = 'US', `addr_state` = 'PA', `addr_city` = 'Pittsburgh', `addr_street` = 'fifth Ave', `addr_zipcode` = '15123', `card_type` = 'VISA', `card_number` = '412342370197810', `card_holder_name` = 'yt', `billing_addr_country` = 'US', `billing_addr_state` = 'PA', `billing_addr_city` = 'Pittsburgh', `billing_addr_street` = 'fifth Ave', `billing_addr_zipcode` = '15123' WHERE (`id` = '1');
    
   -order
    INSERT INTO `infsci`.`order` (`id`, `customer_id`, `datetime`, `addr_name`, `addr_country`, `addr_state`, `addr_city`, `addr_street`, `addr_zipcode`) VALUES ('1', '1', '2020-11-20', 'Apt 101', 'US', 'PA', 'Pittsburgh', 'fifth Ave', '15123');
    INSERT INTO `infsci`.`order` (`id`, `customer_id`, `datetime`, `addr_name`, `addr_country`, `addr_state`, `addr_city`, `addr_street`, `addr_zipcode`) VALUES ('2', '1', '2020-11-19', 'Apt 101', 'US', 'PA', 'Pittsburgh', 'fifth Ave', '15123');
    INSERT INTO `infsci`.`order` (`id`, `customer_id`, `datetime`, `addr_name`, `addr_country`, `addr_state`, `addr_city`, `addr_street`, `addr_zipcode`) VALUES ('3', '1', '2020-11-21', 'Apt 101', 'US', 'PA', 'Pittsburgh', 'fifth Ave', '15123');
    INSERT INTO `infsci`.`order` (`id`, `customer_id`, `datetime`, `addr_name`, `addr_country`, `addr_state`, `addr_city`, `addr_street`, `addr_zipcode`) VALUES ('4', '1', '2020-11-15', 'Apt 101', 'US', 'PA', 'Pittsburgh', 'fifth Ave', '15123');

   -order status
    INSERT INTO `infsci`.`orderstatus` (`id`, `order_id`, `status`, `note`, `datetime`) VALUES ('1', '1', 'delivered', 'none', '2020-11-20 00:00:00');
    INSERT INTO `infsci`.`orderstatus` (`id`, `order_id`, `status`, `note`, `datetime`) VALUES ('2', '2', 'delivered', 'none', '2020-11-19 00:00:00');
    INSERT INTO `infsci`.`orderstatus` (`id`, `order_id`, `status`, `note`, `datetime`) VALUES ('3', '3', 'delivered', 'none', '2020-11-21 00:00:00');
    INSERT INTO `infsci`.`orderstatus` (`id`, `order_id`, `status`, `note`, `datetime`) VALUES ('4', '4', 'ready to delivery', 'text contact when delivered', '2020-11-15 00:00:00');

   -order contains
    INSERT INTO `infsci`.`ordercontains` (`id`, `order_id`, `game_id`) VALUES ('1', '1', '1');
    INSERT INTO `infsci`.`ordercontains` (`id`, `order_id`, `game_id`) VALUES ('2', '1', '2');
    INSERT INTO `infsci`.`ordercontains` (`id`, `order_id`, `game_id`) VALUES ('3', '1', '1');
    INSERT INTO `infsci`.`ordercontains` (`id`, `order_id`, `game_id`) VALUES ('4', '2', '3');
    INSERT INTO `infsci`.`ordercontains` (`id`, `order_id`, `game_id`) VALUES ('5', '3', '10');
    INSERT INTO `infsci`.`ordercontains` (`id`, `order_id`, `game_id`) VALUES ('6', '4', '11');
    INSERT INTO `infsci`.`ordercontains` (`id`, `order_id`, `game_id`) VALUES ('7', '3', '11');
    INSERT INTO `infsci`.`ordercontains` (`id`, `order_id`, `game_id`) VALUES ('8', '2', '2');
    INSERT INTO `infsci`.`ordercontains` (`id`, `order_id`, `game_id`) VALUES ('9', '2', '11');
    INSERT INTO `infsci`.`ordercontains` (`id`, `order_id`, `game_id`) VALUES ('10', '1', '5');
