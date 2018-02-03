#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# 
#
# This file is part of osm-leaderboard
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.


import sqlite3
from datetime import datetime
from flask import Flask, request, render_template
import datetime
app = Flask(__name__)
EVENT_DATE = datetime.datetime.now().date()


@app.route("/", methods=["GET", "POST"])
def handle_register():
    if request.method == "GET":
        # render the form template
        return render_template('register.html')

    elif request.method == "POST":
        osm_display_name = request.form.get('username')
        user_email = request.form.get('email')

        if (osm_display_name and user_email) is not None:
            db_connection = sqlite3.connect('data.sqlite3')
            db_cursor = db_connection.cursor()

            # query db to see if user already exsits
            query = "select display_name from leaderboard where display_name='{}'".format(osm_display_name)
            db_cursor.execute(query)
            row_set = db_cursor.fetchone()

            # by default consider user is registered for sending reponse message
            message = "You have already registered. No need to do it again. Thanks."

            # if the query result is None, then add user
            try:
                if row_set is None:
                    insert_query = "insert into leaderboard (display_name, user_email, last_update) values ('{}', '{}', '{}')"
                    db_cursor.execute(insert_query.format(osm_display_name, user_email, EVENT_DATE))
                    db_connection.commit()
                    message = "Registered. Thanks."
            except sqlite3.IntegrityError as ie:
                print("User already registered: {}".format(ie))

            db_connection.close()

        else:
            message = "OSM Display Name and Email are required."

        return render_template('success.html', message = message)


@app.route("/leaderboard", methods=["GET"])
def handle_leaderboard():
    db_connection = sqlite3.connect('data.sqlite3')
    db_cursor = db_connection.cursor()
    db_cursor.execute("select display_name, current_score, last_update from leaderboard order by -current_score;")
    result_set = db_cursor.fetchall()
    db_connection.close()
    return render_template('leaderboard.html', result_set=result_set)


if __name__ == "__main__":
    app.run(debug=False, host="172.17.0.2", port=8787)
