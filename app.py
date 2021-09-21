from os import name
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
import sqlite3
import json
from pathlib import Path

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'very secret key'
    app.config['DB_URI'] = 'database.db'
    app.config['temp_photo_location'] = 'static/temp_photos/'
    return app


app = create_app()


def get_db_connection():
    conn = sqlite3.connect(app.config['DB_URI'])
    conn.row_factory = sqlite3.Row
    return conn


def get_collection(collection_id):
    conn = get_db_connection()
    collection = conn.execute('SELECT * FROM gallery WHERE id = ?',
                        (collection_id,)).fetchone()
    conn.close()
    if collection is None:
        abort(404)
    return collection


def get_collection_art(collection_id):
    conn = get_db_connection()
    art = conn.execute('SELECT * FROM art WHERE gallery_id = ?',
                        (collection_id,)).fetchall()
    conn.close()
    if art is None:
        abort(404)
    return art


def get_artist(artist_id):
    conn = get_db_connection()
    artist = conn.execute('SELECT * FROM artist WHERE id = ?',
                        (artist_id,)).fetchone()
    conn.close()
    if artist is None:
        abort(404)
    return artist


def get_artist_art(artist):
    conn = get_db_connection()
    art = conn.execute('SELECT * FROM art WHERE artist = ?',
                        (artist,)).fetchall()
    conn.close()
    if art is None:
        abort(404)
    return art


def get_art(art_id):
    conn = get_db_connection()
    art = conn.execute('SELECT * FROM art WHERE id = ?',
                        (art_id,)).fetchone()
    conn.close()
    if art is None:
        abort(404)
    return art


# Utility Functions #
def writeTofile(data, filename):
    with open(filename, 'wb') as file:
        file.write(data)


def convertToBinary(filename):
    with open(filename, 'rb') as file:
        blob = file.read()
    return blob


def parseJSON(filename):
    with open(filename) as file:
        parsed = json.load(file)
    return parsed


# routes #

@app.route('/')
def index():
    conn = get_db_connection()
    collections = conn.execute('SELECT * FROM gallery').fetchall()
    artists = conn.execute('SELECT * FROM artist').fetchall()
    conn.close()
    return render_template('index.html', collections=collections, artists=artists)


@app.route('/collection/<int:collection_id>')
def collection(collection_id):
    collection = get_collection(collection_id)
    art = get_collection_art(collection_id)

    if art:
        for piece in art:
            file_path = Path(app.config['temp_photo_location'] + piece['title'].replace(" ", "_") + ".jpg")
            writeTofile(piece['photo'], file_path)
        return render_template('collection.html', collection=collection, art=art)
    else:
        return render_template('collection_empty.html', collection=collection)
    


@app.route('/artist/<int:artist_id>')
def artist(artist_id):
    artist = get_artist(artist_id)
    art = get_artist_art(artist['full_name'])

    if art:
        for piece in art:
            file_path = Path(app.config['temp_photo_location'] + piece['title'].replace(" ", "_") + ".jpg")
            writeTofile(piece['photo'], file_path)
        return render_template('artist.html', artist=artist, art=art)
    else:
        return render_template('artist_empty.html', artist=artist)


@app.route('/art/add', methods=('GET', 'POST'))
def add_art():
    if request.method == 'POST':
        title = request.form['title']
        artist = request.form['artist']
        created = request.form['created']
        collection = request.form['collection']
        filepath = request.form['filepath']
        summary = request.form['summary']

        if not title or not artist or not created or not collection or not filepath or not summary:
            flash('All fields are required!')
        else:
            conn = get_db_connection()

            query = """INSERT INTO art (title, artist, created, photo, gallery_id, summary) VALUES (?, ?, ?, ?, ?, ?)"""
            photo = convertToBinary(filepath)
            collection = conn.execute('SELECT * FROM gallery WHERE title = ?', (collection,)).fetchone()
            data_tuple = (title, artist, created, photo, collection[0], summary)
            conn.execute(query, data_tuple)

            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template('add_art.html')


@app.route('/artist/add', methods=('GET', 'POST'))
def add_artist():
    if request.method == 'POST':
        full_name = request.form['full_name']
        dob = request.form['dob']
        summary = request.form['summary']

        if not full_name or not dob or not summary:
            flash('All fields are required!')
        else:
            conn = get_db_connection()

            conn.execute("INSERT INTO artist (full_name, dob, summary) VALUES (?, ?, ?)",
            (full_name, dob, summary))

            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template('add_artist.html')


@app.route('/collection/add', methods=('GET', 'POST'))
def add_collection():
    if request.method == 'POST':
        title = request.form['title']
        summary = request.form['summary']

        if not title or not summary:
            flash('All fields are required!')
        else:
            conn = get_db_connection()

            conn.execute("INSERT INTO gallery (title, summary) VALUES (?, ?)",
            (title, summary))

            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template('add_collection.html')


@app.route('/bulk/add', methods=('GET', 'POST'))
def add_bulk():
    if request.method == 'POST':
        filepath = request.form['filepath']

        if not filepath:
            flash('Filepath required!')
        else:
            _add_bulk(filepath)
            return redirect(url_for('index'))
    return render_template('add_bulk.html')


def _add_bulk(filepath):
    parsed = parseJSON(filepath)
    conn = get_db_connection()

    for collection in parsed['collections']:
        conn.execute("INSERT INTO gallery (title, summary) VALUES (?, ?)",
            (collection['title'], collection['summary']))

    for artist in parsed['artists']:
        conn.execute("INSERT INTO artist (full_name, dob, summary) VALUES (?, ?, ?)",
            (artist['full_name'], artist['dob'], artist['summary']))

    conn.commit()

    for art in parsed['art']:
        query = """INSERT INTO art (title, artist, created, photo, gallery_id, summary) VALUES (?, ?, ?, ?, ?, ?)"""
        photo = convertToBinary(art['filepath'])
        collection = conn.execute('SELECT * FROM gallery WHERE title = ?', (art['collection_name'],)).fetchone()
        data_tuple = (art['title'], art['artist'], art['created'], photo, collection[0], art['summary'])
        conn.execute(query, data_tuple)

    conn.commit()
    conn.close()


@app.route('/art/<int:id>/edit', methods=('GET', 'POST'))
def edit_art(id):
    art = get_art(id)

    if request.method == 'POST':
        title = request.form['title']
        artist = request.form['artist']
        created = request.form['created']
        collection = request.form['collection']
        filepath = request.form['filepath']
        summary = request.form['summary']
        
        if not title or not artist or not created or not collection or not summary:
            flash('All fields except filepath are required!')
        else:
            conn = get_db_connection()

            collection = conn.execute('SELECT * FROM gallery WHERE title = ?', (collection,)).fetchone()

            if filepath:
                query = """UPDATE art SET title = ?, artist = ?, created = ?, photo = ?, gallery_id = ?, summary = ? WHERE id = ?"""
                photo = convertToBinary(filepath)
                data_tuple = (title, artist, created, photo, collection[0], summary, id)
            else:
                query = """UPDATE art SET title = ?, artist = ?, created = ?, gallery_id = ?, summary = ? WHERE id = ?"""
                data_tuple = (title, artist, created, collection[0], summary, id)

            conn.execute(query, data_tuple)

            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    else:
        conn = get_db_connection()
        collection = conn.execute('SELECT * FROM gallery WHERE id = ?', (art['gallery_id'],)).fetchone()
        conn.close()

    return render_template('edit_art.html', art=art, collection_name=collection['title'])
    


@app.route('/artist/<int:id>/edit', methods=('GET', 'POST'))
def edit_artist(id):
    artist = get_artist(id)

    if request.method == 'POST':
        full_name = request.form['full_name']
        dob = request.form['dob']
        summary = request.form['summary']

        if not full_name or not dob or not summary:
            flash('All fields are required!')
        else:
            conn = get_db_connection()

            conn.execute("UPDATE artist SET full_name = ?, dob = ?, summary = ? WHERE id = ?",
            (full_name, dob, summary, id))

            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit_artist.html', artist=artist)


@app.route('/collection/<int:id>/edit', methods=('GET', 'POST'))
def edit_collection(id):
    collection = get_collection(id)

    if request.method == 'POST':
        title = request.form['title']
        summary = request.form['summary']

        if not title or not summary:
            flash('All fields are required!')
        else:
            conn = get_db_connection()

            conn.execute("UPDATE gallery SET title = ?, summary = ? WHERE id = ?",
            (title, summary, id))

            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit_collection.html', collection=collection)


@app.route('/art/<int:id>/delete', methods=('POST',))
def delete_art(id):
    art = get_art(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM art WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(art['title']))
    return redirect(url_for('index'))


@app.route('/artist/<int:id>/delete', methods=('POST',))
def delete_artist(id):
    artist = get_artist(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM artist WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(artist['full_name']))
    return redirect(url_for('index'))


@app.route('/collection/<int:id>/delete', methods=('POST',))
def delete_collection(id):
    collection = get_collection(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM gallery WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(collection['title']))
    return redirect(url_for('index'))