# Cura

Cura was heavily inspired by the recent movement of many art galleries towards creating a virtual way to view key collections. While I don't own any notable pieces of art, I have essentially curated my own personal 'art collections' over the years by creating lists of my favourite pieces as I visited museums and read through countless art books.

Currently, Cura is set up to display a few of my favourite art pieces, organized either by period or by artist, but the functionality is there for others to add, delete, or edit any collections, artists, or individual art pieces or bulk add all three at once.

Created using Flask and SQLite with full testing of all endpoints. 

To run Cura, you need to have Flask installed and then run:
```
export FLASK_APP=app
export FLASK_ENV=development
python init_db.py 
flask run
```
To run tests, you also need blinker and pytest installed, then run:
```
pytest
```
