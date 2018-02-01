#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
#
# Copyright 2017 Prasanna Venkadesh
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


import asyncio
import socket
import sqlite3
import xml.etree.ElementTree as eTree

from aiohttp import ClientSession, TCPConnector


def parse_osmChange_xml(xml_data):
    """
    Count the number of contributions in a given changeset

    :param str xml_data: changset xml to parse
    :return: number of changes in changeset
    :rtype: int
    """
    root = eTree.fromstring(xml_data)
    if len(root) != 0:
        return len(root)


async def fetch_osmChange(changeset_id, session):
    """
    Asynchronously fetch xml data for a given changeset id

    :param str changeset_id: the id to fetch xml for
    :param object session: aiohttp client session

    :return: xml response
    :rtype: str
    """
    url = OSMCHANGE_URL.format(changeset_id)
    print(url)
    async with session.get(url) as response:
        response_content = await response.read()
        return response_content


async def parse_changeset_xml(xml_data, session, cursor):
    """
    Parse changesets for a user and update their contribution in 
    database.

    :param str xml_data: changeset xml data to parse
    :param object session: aiohttp client session
    :param object cursor: sqlite3 cursor to execute query
    """
    changeset_ids = []
    try:
        root = eTree.fromstring(xml_data)
        if len(root) != 0:
            last_update = root[0].attrib.get('created_at')
            user_name = root[0].attrib.get('user')
            for change_set in root:
                changeset_ids.append(int(change_set.attrib.get('id')))

            # reverse because to parse from oldest to newest first
            changeset_ids.reverse()

            # get previous count from db
            cursor.execute("select current_score, mr_cid from leaderboard where display_name='{}';".format(user_name))
            row = cursor.fetchone()
            if row:
                count = int(row[0])
                # get most_recent_changeset_id from db
                mr_cid = int(row[1])

            if changeset_ids[-1] != mr_cid:
                osmChange_tasks = []
                for changset_id in changeset_ids:
                    if changset_id is not None:
                        if changset_id > mr_cid:
                            print("Hitting %s of %s" %(changset_id, user_name))
                            osmChange_task = asyncio.ensure_future(fetch_osmChange(changset_id, session))
                            osmChange_tasks.append(osmChange_task)

                osmChange_responses = await asyncio.gather(*osmChange_tasks)
                for osmChange_response in osmChange_responses:
                    new_count = parse_osmChange_xml(osmChange_response)
                    count = count + new_count

                mr_cid = changeset_ids[-1]
                print(mr_cid, user_name, count)
                #update mr_cid & count value in db for this user
                cursor.execute("update leaderboard set current_score={}, mr_cid='{}', last_update='{}' where display_name='{}';".format(count, mr_cid, last_update, user_name))
    except Exception as ex:
        print (ex, xml_data)


async def fetch_changeset(user_name, last_time, session):
    """
    Asynchronously fetch changesets for a user for a given date

    :param str user_name: username to fetch changeset for
    :param str last_time: date of last fetch for this user
    :param object session: aiohttp client session

    :return: changeset xml response
    :rtype: str
    """
    url = BASE_URL.format(user_name, last_time)
    print(url)
    async with session.get(url) as response:
        return await response.read()


async def main(loop):
    db_connection = sqlite3.connect('data.sqlite3')
    db_cursor = db_connection.cursor()

    db_cursor.execute("select display_name, last_update from leaderboard;")
    row_set = db_cursor.fetchall()

    connector = TCPConnector(family=socket.AF_INET)
    async with ClientSession(loop=loop, connector=connector) as session:
        tasks = [asyncio.ensure_future(fetch_changeset(row[0], row[1], session)) for row in row_set]
        responses = await asyncio.gather(*tasks)

        new_tasks = [asyncio.ensure_future(parse_changeset_xml(response, session, db_cursor)) for response in responses]
        await asyncio.gather(*new_tasks)

    db_connection.commit()
    db_connection.close()

    connector.close()

if __name__ == "__main__":
    BASE_URL = "http://api.openstreetmap.org/api/0.6/changesets?display_name={}"
    OSMCHANGE_URL = "http://api.openstreetmap.org/api/0.6/changeset/{}/download"

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
