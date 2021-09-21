from os import name
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
import sqlite3
from pathlib import Path


app = Flask(__name__)
app.config['SECRET_KEY'] = 'very secret key'

def get_db_connection():
    conn = sqlite3.connect('database.db')
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

    for piece in art:
        file_path = Path("static/temp_photos/" + piece['title'].replace(" ", "_") + ".jpg")
        if not file_path.is_file():
            writeTofile(piece['photo'], file_path)
            
    return render_template('collection.html', collection=collection, art=art)


@app.route('/artist/<int:artist_id>')
def artist(artist_id):
    artist = get_artist(artist_id)
    art = get_artist_art(artist['full_name'])

    for piece in art:
        file_path = Path("static/temp_photos/" + piece['title'].replace(" ", "_") + ".jpg")
        if not file_path.is_file():
            writeTofile(piece['photo'], file_path)
    return render_template('artist.html', artist=artist, art=art)


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
            collection_id = conn.execute('SELECT * FROM gallery WHERE title = ?', (collection,)).fetchone()
            data_tuple = (title, artist, created, photo, collection_id, summary)
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

            collection_id = conn.execute('SELECT * FROM gallery WHERE title = ?', (collection,)).fetchone()

            if filepath:
                query = "'UPDATE art SET title = ?, artist = ?, created = ?, photo = ?, gallery_id = ?, summary = ? WHERE id = ?'"
                photo = convertToBinary(filepath)
                data_tuple = (title, artist, created, photo, collection_id, summary, id)
            else:
                query = "'UPDATE art SET title = ?, artist = ?, created = ?, gallery_id = ?, summary = ? WHERE id = ?'"
                data_tuple = (title, artist, created, collection_id, summary, id)

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