from flask import Flask, jsonify, render_template, Blueprint, request, make_response, send_file, redirect
from urllib import quote
import six
import base64
import requests
import json
import os
import sqlite3
from settings import APP_STATIC

app = Flask(__name__)

client_id = '01892cb58b67493e98cf46e7f46b39ae'
client_secret = 'aeb740a9ac564ee89eafa84df33a94ed'
callback = 'http%3A%2F%2Fadventify.davidlips.onl%2Fcallback'

@app.route('/')
def init():
    return redirect('https://accounts.spotify.com/authorize/?client_id=' + client_id + '&response_type=code&scope=playlist-modify-public%20playlist-read-private%20playlist-read-collaborative%20user-read-private%20user-read-email&redirect_uri=' + callback)

@app.route('/callback')
def main():
    try:
        code = request.args.get("code")
        if(code):
            r = requests.post('https://accounts.spotify.com/api/token', data={'grant_type': 'authorization_code', 'code': code, 'redirect_uri': callback, 'client_secret': client_secret, 'client_id': client_id})
            if(r):
                    access = r.json()
                    access_token = access['access_token']
                    refresh_token = access['refresh_token']

                    r = requests.get('https://api.spotify.com/v1/me', headers={'Authorization': 'Bearer ' + access_token})
                    if(r):
                            user = r.json()

                            r = requests.get('https://api.spotify.com/v1/users/' + user['id'] + '/playlists', headers={'Authorization': 'Bearer ' + access_token})
                            if(r):
                                    return render_template('/index.html', access=access, user=user, playlists=r.json())
                            else:
                                    return render_template('/error.html')
                    else:
                            return render_template('/error.html')
            else:
                    return render_template('/error.html')
        else:
            return render_template('/error.html')
    except:
        return render_template('/error.html')

def createPlaylist(plt, splt, access, user):
	c = sqlite3.connect(os.path.join(APP_STATIC, 'db/metadata.db'))
	conn = c.cursor()
	conn.execute('INSERT INTO playlists VALUES (?,?,?,?,?)', (plt['id'], splt['id'], access['access_token'], access['refresh_token'], user['id'],))
	c.commit()
	c.close()

@app.route('/create', methods=['POST'])
def create():
	try:
		req = request.get_json()
		r = requests.post('https://api.spotify.com/v1/users/' + req['user']['id'] + '/playlists', headers={'Authorization': 'Bearer ' + req['access']['access_token'], 'Content-Type': 'application/json'}, data=json.dumps({'name': req['name']}))
		res = r.json()
		createPlaylist(res, req['secret'], req['access'], req['user'])

		secret = requests.get('https://api.spotify.com/v1/users/' + req['user']['id']  + '/playlists/' + req['secret']['id'], headers={'Authorization': 'Bearer ' + req['access']['access_token']})

	
        	playlist = requests.get('https://api.spotify.com/v1/users/' + req['user']['id'] + '/playlists/' + res['id'], headers={'Authorization': 'Bearer ' + req['access']['access_token']})

	        newIndex = len(playlist.json()['tracks']['items'])
		print(newIndex)
      	 	if(newIndex < len(secret.json()['tracks']['items'])):
         		rs = requests.get('https://api.spotify.com/v1/tracks/' + secret.json()['tracks']['items'][newIndex]['track']['id'])
               		uri = rs.json()['uri']
	                rs = requests.post('https://api.spotify.com/v1/users/' + req['user']['id'] + '/playlists/' + res['id'] + '/tracks', headers={"Authorization": "Bearer " + req['access']['access_token'], "Content-Type": "application/json"}, data=json.dumps({"uris": [uri]}))

		return jsonify(r.json()), 200
	except Exception as e:
		return jsonify({"error": str(e)}), 400

@app.route('/playlist')
@app.route('/playlist/<pid>')
def playlist(pid=None):
	try:
		if(pid == None):
			return render_template('/error.html')
		## get current track and count
		c = sqlite3.connect(os.path.join(APP_STATIC, 'db/metadata.db'))
       		conn = c.cursor()
		conn.execute('SELECT * FROM playlists WHERE pid=?', (pid,))
		result = conn.fetchone()
		refresh_token = result[3]
		user_id = result[4]
		sid = result[1]
 	        c.commit()
        	c.close()

		r = requests.post('https://accounts.spotify.com/api/token', data={'grant_type': 'refresh_token', 'refresh_token': refresh_token}, headers={'Authorization': 'Basic ' + base64.b64encode(six.text_type(client_id + ':' + client_secret).encode('ascii')).decode('ascii')})

		access_token = r.json()['access_token']

		r = requests.get('https://api.spotify.com/v1/users/' + user_id  + '/playlists/' + sid, headers={'Authorization': 'Bearer ' + access_token})
	
		spltLength = len(r.json()['tracks']['items'])

		r = requests.get('https://api.spotify.com/v1/users/' + user_id  + '/playlists/' + pid, headers={'Authorization': 'Bearer ' + access_token})

		pltLength = len(r.json()['tracks']['items'])

		remainingDays = 1 + spltLength - pltLength	
	
		return render_template('/playlist.html', track=(r.json()['tracks']['items'][-1] if pltLength > 0 else "false"), remaining=remainingDays)
	except:
		return render_template('/error.html')
		

if __name__ == "__main__":
    app.run(host='0.0.0.0')
