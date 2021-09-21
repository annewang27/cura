import pytest
import sqlite3
import logging
from flask import template_rendered
import os

from app import app, convertToBinary


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config['DB_URI'] = 'test.db'
    app.config['temp_photo_location'] = 'static/test/temp_photos/'

    connection = sqlite3.connect(app.config['DB_URI'])
    with open('schema.sql') as f:
        connection.executescript(f.read())

    with app.test_client() as client:
        yield client

    dir = 'static/test/temp_photos/'
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))


# code from from https://medium.com/analytics-vidhya/how-to-test-flask-applications-aef12ae5181c 
@pytest.fixture
def captured_templates():
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


@pytest.fixture
def add_artists():
    connection = sqlite3.connect(app.config['DB_URI'])
    
    connection.execute("INSERT INTO artist (full_name, dob, summary) VALUES (?, ?, ?)",
        ("Artist 1", "January 1, 20000", "Artist 1 description"))
    connection.execute("INSERT INTO artist (full_name, dob, summary) VALUES (?, ?, ?)",
        ("Artist 2", "February 1, 20000", "Artist 2 description"))
    connection.execute("INSERT INTO artist (full_name, dob, summary) VALUES (?, ?, ?)",
        ("Artist 3", "March 1, 20000", "Artist 3 description"))
    
    connection.commit()
    connection.close()


@pytest.fixture
def add_collections():
    connection = sqlite3.connect(app.config['DB_URI'])
    
    connection.execute("INSERT INTO gallery (title, summary) VALUES (?, ?)",
        ("Collection 1", "Collection 1 summary"))
    connection.execute("INSERT INTO gallery (title, summary) VALUES (?, ?)",
        ("Collection 2", "Collection 2 summary"))
    
    connection.commit()
    connection.close()


@pytest.fixture
def add_art(add_collections):
    connection = sqlite3.connect(app.config['DB_URI'])

    query = """INSERT INTO art (title, artist, created, photo, gallery_id, summary) VALUES (?, ?, ?, ?, ?, ?)"""
    photo = convertToBinary('tests/files/test1.jpeg')
    collection = connection.execute('SELECT * FROM gallery WHERE title = ?', ('Collection 1',)).fetchone()
    data_tuple = ("Art 1", "Artist 1", "2021", photo, collection[0], "Art 1 summary")
    connection.execute(query, data_tuple)

    query = """INSERT INTO art (title, artist, created, photo, gallery_id, summary) VALUES (?, ?, ?, ?, ?, ?)"""
    photo = convertToBinary('tests/files/test2.jpeg')
    collection = connection.execute('SELECT * FROM gallery WHERE title = ?', ('Collection 1',)).fetchone()
    data_tuple = ("Art 2", "Artist 2", "2021", photo, collection[0], "Art 2 summary")
    connection.execute(query, data_tuple)

    query = """INSERT INTO art (title, artist, created, photo, gallery_id, summary) VALUES (?, ?, ?, ?, ?, ?)"""
    photo = convertToBinary('tests/files/test3.jpeg')
    collection = connection.execute('SELECT * FROM gallery WHERE title = ?', ('Collection 1',)).fetchone()
    data_tuple = ("Art 3", "Artist 2", "2021", photo, collection[0], "Art 3 summary")
    connection.execute(query, data_tuple)
    
    connection.commit()
    connection.close()