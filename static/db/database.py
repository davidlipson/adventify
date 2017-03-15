import sqlite3

c = sqlite3.connect('metadata.db')

conn = c.cursor()

conn.execute('DROP TABLE IF EXISTS playlists')

conn.execute('CREATE TABLE playlists (pid, sid, access, refresh, user)')

c.commit()
c.close()
