from flask import Flask, send_file, request
import os, subprocess
app = Flask(__name__)

@app.route('/')
def root():
    return 'ZEMALA 12/12 gruen - <a href="/board">/board</a> - <a href="/send">/send</a>'

@app.route('/board')
def board():
    # nimmt dein control_board.html falls vorhanden, sonst send hub
    for p in ['~/zemala/control_board.html','~/zemala/zemala_send_hub.html','./control_board.html']:
        fp=os.path.expanduser(p)
        if os.path.exists(fp):
            return send_file(fp)
    return 'board nicht gefunden - lege control_board.html nach ~/zemala/'

@app.route('/send')
def sendhub():
    return send_file(os.path.expanduser('~/zemala/zemala_send_hub_feierabend.html')) if os.path.exists(os.path.expanduser('~/zemala/zemala_send_hub_feierabend.html')) else 'send hub fehlt'

@app.route('/api/flashlight/<state>')
def flash(state):
    try:
        subprocess.run(['termux-torch', state], timeout=3)
        return f'torch {state}'
    except Exception as e:
        return f'torch fail {e} - install Termux:API APK from https://f-droid.org/packages/com.termux.api/'

@app.route('/api/search')
def search():
    q=request.args.get('q','Vortex Hamburg HBF')
    try:
        subprocess.run(['termux-open-url', f'https://www.google.com/search?q={q}'], timeout=3)
    except:
        pass
    return f'search {q}'

@app.route('/api/rclone/sync')
def sync():
    os.system('export RCLONE_CONFIG_PASS=zemalasenzar && rclone copy gdrive_zemala:Zemala_loop ~/zemala/ --progress &')
    return 'sync started'

if __name__=='__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
