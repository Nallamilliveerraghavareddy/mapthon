osm-leaderboard
=====

Deploy this web application written in python-flask to organize OpenStreetMap Mapathon. This application was primarily written for [Swecha] to organize one such [OSM mapathon](http://osm-leaderboard.fsftn.org).

Note: **Python 3.6** is required to run the `background_runner.py` file as it is written **asynchronously** using the Python's new famous standard library called `asyncio` and `aiohttp`. At the time of writing this document,
python3.6 has to be manually compiled from source code. Compiling python from source is not a daunting task, if you installed the dependent libraraies properly.
[This blog](https://solarianprogrammer.com/2017/06/30/building-python-ubuntu-wsl-debian/) should be helpful to do that.


**Installing Dependencies for osm-leaderboard**

    pip3.6 install -r requirements.txt


**Setup backend**

I have used sqlite3 for data-storage at the backend as it is light-weight and is more than sufficient for this kind of applications. Create the database by running the following command. Make sure, you have `sqlite3`
command line interface installed.

    sqlite3 data.sqlite3 < leaderboard.sql

If you give a different name for the sqlite3 database file, make sure you change in the python file too (both `app.py` and `background_runner.py`)


**Starting the application**

You might be organizing your mapathon starting from a particular date. This date has to be set in the `EVENT_DATE` variable in the file `app.py`, before proceedin further.

    python app.py

for deploying in production or realtime, you can use any one of the multi-threaded, mutli-processing libraries like `gunicorn` or `gevent`. I prefer installing `gunicorn` using `pip` and starting the application like the following

    gunicorn -D -w 2 -b 127.0.0.1:8787 app:app

The app should now be started and running. You can access the application by visiting http://localhost:8787 in your browser.


leaderboard registration
======

Registration is a 2 step process.
- In step 1 users are asked to enter their **OSM** account user name (a.k.a. **Display Name**).
- In step 2 users are asked to enter their email address, so that organizers could communicate with them later.


leaderboard update
======

The actual updates to leaderboard will happen only via `background_runner.py` program. This file has to be invoked using **python3.6** (not even python3.5) manually like this.

    python3.6 background_runner.py

- `background_runner.py` hits the osm's api server for fetching **changesets** of a particular user using their display name asynchronously.
- the changesets are then parsed for changeset ids.
- the program will then again hit osm's api server for fetching details of a particular changeset id and the user's leaderboard is updated accordingly.

**Scheduling leaderboard updates**

Instead of running the `background_runner.py` manually, the program can be scheduled at regular intervals or specified time using utilities like **crontab**. Look at the `cron_sample` for an example.


Contributors
====
1.swecha


License
===

This project is license under **GPL v3** copyleft license. Read `LICENSE` file for more infomration.
