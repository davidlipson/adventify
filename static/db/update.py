import json
import requests
import six, base64
import sqlite3

client_id = '01892cb58b67493e98cf46e7f46b39ae'
client_secret = 'aeb740a9ac564ee89eafa84df33a94ed'

c = sqlite3.connect('metadata.db')
conn = c.cursor()

conn.execute('select * from playlists')

rows = conn.fetchall()
for r in rows:
	try:
		pid, sid, refresh_token, user_id = r[0], r[1], r[3], r[4]
		r = requests.post('https://accounts.spotify.com/api/token', data={'grant_type': 'refresh_token', 'refresh_token': refresh_token}, headers={'Authorization': 'Basic ' + base64.b64encode(six.text_type(client_id + ':' + client_secret).encode('ascii')).decode('ascii')})

        	access_token = r.json()['access_token']	

		secret = requests.get('https://api.spotify.com/v1/users/' + user_id  + '/playlists/' + sid, headers={'Authorization': 'Bearer ' + access_token})
	

		playlist = requests.get('https://api.spotify.com/v1/users/' + user_id  + '/playlists/' + pid, headers={'Authorization': 'Bearer ' + access_token})

		newIndex = len(playlist.json()['tracks']['items'])
		if(newIndex < len(secret.json()['tracks']['items'])):
			r = requests.get('https://api.spotify.com/v1/tracks/' + secret.json()['tracks']['items'][newIndex]['track']['id'])
			uri = r.json()['uri']
			print(uri)
			r = requests.post('https://api.spotify.com/v1/users/' + user_id + '/playlists/' + pid + '/tracks', headers={"Authorization": "Bearer " + access_token, "Content-Type": "application/json"}, data=json.dumps({"uris": [uri]}))
			print(r.json())
	except:
		pass
c.commit()
c.close()
