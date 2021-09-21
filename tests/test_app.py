import sqlite3

from app import app, convertToBinary


def test_index(client, captured_templates, add_art, add_artists) -> None:
    route = "/"
    rv = client.get(route)

    assert rv.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "index.html"

    assert len(context["collections"]) == 2
    assert len(context["artists"]) == 3


def test_collection(client, captured_templates, add_art) -> None:
    connection = sqlite3.connect(app.config['DB_URI'])
    collection = connection.execute('SELECT * FROM gallery WHERE title = ?', ('Collection 1',)).fetchone()
    connection.close()

    route = "/collection/" + str(collection[0])
    rv = client.get(route)

    assert rv.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "collection.html"

    assert context["collection"][0] == collection[0]
    assert len(context["art"]) == 3


def test_empty_collection(client, captured_templates, add_art) -> None:
    connection = sqlite3.connect(app.config['DB_URI'])
    collection = connection.execute('SELECT * FROM gallery WHERE title = ?', ('Collection 2',)).fetchone()
    connection.close()

    route = "/collection/" + str(collection[0])
    rv = client.get(route)

    assert rv.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "collection_empty.html"

    assert context["collection"][0] == collection[0]
    
    
def test_artist(client, captured_templates, add_art, add_artists) -> None:
    connection = sqlite3.connect(app.config['DB_URI'])
    artist = connection.execute('SELECT * FROM artist WHERE full_name = ?', ('Artist 2',)).fetchone()
    connection.close()

    route = "/artist/" + str(artist[0])
    rv = client.get(route)

    assert rv.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "artist.html"

    assert context["artist"][0] == artist[0]
    assert len(context["art"]) == 2


def test_empty_artist(client, captured_templates, add_art, add_artists) -> None:
    connection = sqlite3.connect(app.config['DB_URI'])
    artist = connection.execute('SELECT * FROM artist WHERE full_name = ?', ('Artist 3',)).fetchone()
    connection.close()

    route = "/artist/" + str(artist[0])
    rv = client.get(route)

    assert rv.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "artist_empty.html"

    assert context["artist"][0] == artist[0]


def test_get_add_artist(client, captured_templates) -> None:
    route = "/artist/add"
    rv = client.get(route)

    assert rv.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "add_artist.html"


def test_post_add_artist(client, captured_templates) -> None:
    route = "/artist/add"
    rv = client.post(route, data=dict(
        full_name="Artist 4",
        dob="April 1, 2000",
        summary="Artist 4 description"
    ), follow_redirects=True)

    assert rv.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "index.html"

    connection = sqlite3.connect(app.config['DB_URI'])
    artist = connection.execute('SELECT * FROM artist WHERE full_name = ?', ('Artist 4',)).fetchone()
    connection.close()

    assert artist[1] == "Artist 4"


def test_get_add_art(client, captured_templates, add_collections) -> None:
    route = "/art/add"
    rv = client.get(route)

    assert rv.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "add_art.html"


def test_post_add_art(client, captured_templates, add_collections) -> None:
    route = "/art/add"
    rv = client.post(route, data=dict(
        title="Art 4",
        artist="Artist 1",
        created="2021",
        collection='Collection 1',
        summary="Art 4 Summary",
        filepath='tests/files/test4.jpeg'
    ), follow_redirects=True)

    assert rv.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "index.html"

    connection = sqlite3.connect(app.config['DB_URI'])
    art = connection.execute('SELECT * FROM art WHERE title = ?', ('Art 4',)).fetchone()
    connection.close()

    assert art[1] == "Art 4"


def test_get_add_collection(client, captured_templates) -> None:
    route = "/collection/add"
    rv = client.get(route)

    assert rv.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "add_collection.html"


def test_post_add_collection(client, captured_templates) -> None:
    route = "/collection/add"
    rv = client.post(route, data=dict(
        title="Collection 4",
        summary="Collection 4 description"
    ), follow_redirects=True)

    assert rv.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "index.html"

    connection = sqlite3.connect(app.config['DB_URI'])
    collection = connection.execute('SELECT * FROM gallery WHERE title = ?', ('Collection 4',)).fetchone()
    connection.close()

    assert collection[1] == "Collection 4"


def test_get_add_bulk(client, captured_templates) -> None:
    route = "/bulk/add"
    rv = client.get(route)

    assert rv.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "add_bulk.html"


def test_post_add_full_bulk(client, captured_templates) -> None:
    route = "/bulk/add"
    rv = client.post(route, data=dict(
        filepath="tests/files/full_bulk.json"
    ), follow_redirects=True)

    assert rv.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "index.html"

    connection = sqlite3.connect(app.config['DB_URI'])
    collections = connection.execute('SELECT * FROM gallery').fetchall()
    artists = connection.execute('SELECT * FROM artist').fetchall()
    art = connection.execute('SELECT * FROM art').fetchall()
    connection.close()

    assert len(collections) == 2
    assert len(artists) == 1
    assert len(art) == 2


def test_post_add_partial_bulk(client, captured_templates) -> None:
    route = "/bulk/add"
    rv = client.post(route, data=dict(
        filepath="tests/files/partial_bulk.json"
    ), follow_redirects=True)

    assert rv.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "index.html"

    connection = sqlite3.connect(app.config['DB_URI'])
    collections = connection.execute('SELECT * FROM gallery').fetchall()
    artists = connection.execute('SELECT * FROM artist').fetchall()
    art = connection.execute('SELECT * FROM art').fetchall()
    connection.close()

    assert len(collections) == 2
    assert len(artists) == 0
    assert len(art) == 2


def test_post_add_limited_bulk(client, captured_templates) -> None:
    route = "/bulk/add"
    rv = client.post(route, data=dict(
        filepath="tests/files/limited_bulk.json"
    ), follow_redirects=True)

    assert rv.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "index.html"

    connection = sqlite3.connect(app.config['DB_URI'])
    collections = connection.execute('SELECT * FROM gallery').fetchall()
    artists = connection.execute('SELECT * FROM artist').fetchall()
    art = connection.execute('SELECT * FROM art').fetchall()
    connection.close()

    assert len(collections) == 2
    assert len(artists) == 0
    assert len(art) == 0


def test_get_edit_artist(client, captured_templates, add_artists) -> None:
    connection = sqlite3.connect(app.config['DB_URI'])
    artist = connection.execute('SELECT * FROM artist WHERE full_name = ?', ('Artist 2',)).fetchone()
    connection.close()

    route = "/artist/" + str(artist[0]) + "/edit"
    rv = client.get(route)

    assert rv.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "edit_artist.html"

    assert context["artist"][1] == artist[1]


def test_post_edit_artist(client, captured_templates, add_artists) -> None:
    connection = sqlite3.connect(app.config['DB_URI'])
    artist = connection.execute('SELECT * FROM artist WHERE full_name = ?', ('Artist 2',)).fetchone()
    connection.close()

    route = "/artist/" + str(artist[0]) + "/edit"
    rv = client.post(route, data=dict(
        full_name="Artist 2 new",
        dob="February 1, 2000",
        summary="Artist 2 description"
    ), follow_redirects=True)

    assert rv.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "index.html"

    connection = sqlite3.connect(app.config['DB_URI'])
    artist = connection.execute('SELECT * FROM artist WHERE id = ?', (artist[0],)).fetchone()
    connection.close()

    assert artist[1] == "Artist 2 new"


def test_get_edit_collection(client, captured_templates, add_collections) -> None:
    connection = sqlite3.connect(app.config['DB_URI'])
    collection = connection.execute('SELECT * FROM gallery WHERE title = ?', ('Collection 2',)).fetchone()
    connection.close()

    route = "/collection/" + str(collection[0]) + "/edit"
    rv = client.get(route)

    assert rv.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "edit_collection.html"

    assert context["collection"][1] == collection[1]


def test_post_edit_collection(client, captured_templates, add_collections) -> None:
    connection = sqlite3.connect(app.config['DB_URI'])
    collection = connection.execute('SELECT * FROM gallery WHERE title = ?', ('Collection 2',)).fetchone()
    connection.close()

    route = "/collection/" + str(collection[0]) + "/edit"
    rv = client.post(route, data=dict(
        title="Collection 2 new",
        summary="Collection 2 description"
    ), follow_redirects=True)

    assert rv.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "index.html"

    connection = sqlite3.connect(app.config['DB_URI'])
    collection = connection.execute('SELECT * FROM gallery WHERE id = ?', (collection[0],)).fetchone()
    connection.close()

    assert collection[1] == "Collection 2 new"


def test_get_edit_art(client, captured_templates, add_art) -> None:
    connection = sqlite3.connect(app.config['DB_URI'])
    art = connection.execute('SELECT * FROM art WHERE title = ?', ('Art 2',)).fetchone()
    collection = connection.execute('SELECT * FROM gallery WHERE id = ?', (art[4],)).fetchone()
    connection.close()

    route = "/art/" + str(art[0]) + "/edit"
    rv = client.get(route)

    assert rv.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "edit_art.html"

    assert context["art"][1] == art[1]
    assert context["collection_name"] == collection[1]


def test_post_edit_art_no_file(client, captured_templates, add_art) -> None:
    connection = sqlite3.connect(app.config['DB_URI'])
    art = connection.execute('SELECT * FROM art WHERE title = ?', ('Art 2',)).fetchone()
    connection.close()

    route = "/art/" + str(art[0]) + "/edit"
    rv = client.post(route, data=dict(
        title="Art 2 new",
        artist="Artist 1",
        created="2021",
        collection='Collection 1',
        summary="Art 2 Summary",
        filepath=''
    ), follow_redirects=True)

    assert rv.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "index.html"

    connection = sqlite3.connect(app.config['DB_URI'])
    art = connection.execute('SELECT * FROM art WHERE id = ?', (art[0],)).fetchone()
    connection.close()

    assert art[1] == "Art 2 new"


def test_post_edit_art_with_file(client, captured_templates, add_art) -> None:
    connection = sqlite3.connect(app.config['DB_URI'])
    art = connection.execute('SELECT * FROM art WHERE title = ?', ('Art 2',)).fetchone()
    connection.close()

    route = "/art/" + str(art[0]) + "/edit"
    rv = client.post(route, data=dict(
        title="Art 2 new",
        artist="Artist 1",
        created="2021",
        collection='Collection 1',
        summary="Art 2 Summary",
        filepath='tests/files/test4.jpeg'
    ), follow_redirects=True)

    assert rv.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "index.html"

    connection = sqlite3.connect(app.config['DB_URI'])
    art = connection.execute('SELECT * FROM art WHERE id = ?', (art[0],)).fetchone()
    connection.close()

    assert art[1] == "Art 2 new"


def test_delete_artist(client, captured_templates, add_artists) -> None:
    connection = sqlite3.connect(app.config['DB_URI'])
    artist = connection.execute('SELECT * FROM artist WHERE full_name = ?', ('Artist 2',)).fetchone()
    artists_initial = connection.execute('SELECT * FROM artist').fetchall()
    connection.close()

    route = "/artist/" + str(artist[0]) + "/delete"
    rv = client.post(route, follow_redirects=True)

    assert rv.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "index.html"

    connection = sqlite3.connect(app.config['DB_URI'])
    artists_final = connection.execute('SELECT * FROM artist').fetchall()
    connection.close()

    assert len(artists_initial) == 3
    assert len(artists_final) == 2


def test_delete_collections(client, captured_templates, add_collections) -> None:
    connection = sqlite3.connect(app.config['DB_URI'])
    collection = connection.execute('SELECT * FROM gallery WHERE title = ?', ('Collection 2',)).fetchone()
    collections_initial = connection.execute('SELECT * FROM gallery').fetchall()
    connection.close()

    route = "/collection/" + str(collection[0]) + "/delete"
    rv = client.post(route, follow_redirects=True)

    assert rv.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "index.html"

    connection = sqlite3.connect(app.config['DB_URI'])
    collections_final = connection.execute('SELECT * FROM gallery').fetchall()
    connection.close()

    assert len(collections_initial) == 2
    assert len(collections_final) == 1


def test_delete_art(client, captured_templates, add_art) -> None:
    connection = sqlite3.connect(app.config['DB_URI'])
    art = connection.execute('SELECT * FROM art WHERE title = ?', ('Art 2',)).fetchone()
    art_initial = connection.execute('SELECT * FROM art').fetchall()
    connection.close()

    route = "/art/" + str(art[0]) + "/delete"
    rv = client.post(route, follow_redirects=True)

    assert rv.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "index.html"

    connection = sqlite3.connect(app.config['DB_URI'])
    art_final = connection.execute('SELECT * FROM art').fetchall()
    connection.close()

    assert len(art_initial) == 3
    assert len(art_final) == 2