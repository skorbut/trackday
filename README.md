# trackday

A small race monitor for carrera digital.

## Setup

Trackday uses a SQLite database to store race and driver data. Initialize/reset the database via:

```sh
. ./venv/bin/activate
rm app.db
rm -rf migrations
flask db init
flask db migrate
flask db upgrade
flask seed
```

Run the server locally via virtualenv
```sh
. ./venv/bin/activate
flask run
```

Point your browser at http://127.0.0.1:5000 to access the app
