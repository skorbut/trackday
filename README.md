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

### Localization

Wrap all strings to be localized in `_l()` calls. For templates use: `{{ _() }}`

Initialize babel via `pybabel extract -F babel.cfg -k _l -o messages.pot .`. Generate the german language catalog via `pybabel init -i messages.pot -d app/translations -l de`. Compile the language files via `pybabel compile -d app/translations`.

To update the translation do `pybabel extract -F babel.cfg -k _l -o messages.pot .` to collect new translation, update the language files via `pybabel update -i messages.pot -d app/translations`. After that you need to recompile using `pybabel compile -d app/translations`.

### USB Serial Connection on Mac

You can check via `ioreg -c IOSerialBSDClient | grep usb` where the serial connection is available.

### Update the raspberrypi

- connect to raspberrypi via the deploy user using `ssh deploy@raspberrypi`
- change to trackday directory and pull the latest changes from git
- restart the server via `sudo supervisorctl restart trackday`


## Changes

### 20200209 - new driver cockpit
Get rid of the digit display for fuel levels - integrate gauge.js to display fuel levels
Calculate sleep time for cu request thread based on current track status

### 20190915 - denormalize Laps

In order to fetch racer and car based statistics the lap information must be denormalized:
```
flask shell
for r in Race.query.all():
    r.denormalize_laps()
```
