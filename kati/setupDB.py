import sqlite3


class DB_connect():
    def __init__(self, db_name):
        self.connection = sqlite3.connect(f"{db_name}.db")

        self.cur = self.connection.cursor()

    def insert_data(self, values):
        self.cur.execute(
            """ INSERT INTO video(title, url, file_size, resolution, author, views) VALUES(?, ?, ?, ?, ?, ?)""", values)

        self.connection.commit()

    def setupDB(self):
        self.cur.execute("""
          CREATE TABLE video(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title CHAR(255),
            url CHAR(255),
            file_size CHAR(255),
            resolution CHAR(255),
            author CHAR(255),
            views INTEGER
          )
        """)
        self.connection.commit()

    def get_data(self):
        self.cur.execute("""SELECT * FROM video""")
        return self.cur.fetchall()

    def close_conn(self):
        self.connection.close()
