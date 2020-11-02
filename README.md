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

## How to run

### Win
```
set FLASK_APP=project
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
