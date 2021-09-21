import sqlite3

def convertToBinary(filename):
    with open(filename, 'rb') as file:
        blob = file.read()
    return blob


connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

query = """INSERT INTO art (title, artist, created, photo, gallery_id, summary) VALUES (?, ?, ?, ?, ?, ?)"""
photo = convertToBinary('images/persistence_of_mem.jpeg')
data_tuple = ('The Persistence of Memory', 'Salvador Dali', '1931', photo, '1', 'very cool piece')
cur.execute(query, data_tuple)

query = """INSERT INTO art (title, artist, created, photo, gallery_id, summary) VALUES (?, ?, ?, ?, ?, ?)"""
photo = convertToBinary('images/starry_night.jpeg')
data_tuple = ('The Starry Night', 'Vincent van Gogh', '1889', photo, '1', 'very interesting piece')
cur.execute(query, data_tuple)

cur.execute("INSERT INTO gallery (title, summary) VALUES (?, ?)",
            ('cool art', 'art of the past')
            )

cur.execute("INSERT INTO gallery (title, summary) VALUES (?, ?)",
            ('best art', 'art of the future')
            )

cur.execute("INSERT INTO artist (full_name, dob, summary) VALUES (?, ?, ?)",
            ('Salvador Dali', 'May 11, 1904', 'cool artist')
            )

cur.execute("INSERT INTO artist (full_name, dob, summary) VALUES (?, ?, ?)",
            ('Vincent van Gogh', 'March 30, 1853', 'another cool artist')
            )

connection.commit()
connection.close()