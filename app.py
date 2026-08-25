#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ZEMALA Core - Flask Telemetry & Dashboard Server [Stufe 100]

import os
import json
from flask import Flask, jsonify, send_from_directory

app = Flask(__name__, static_folder='.')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/telemetry.json')
def get_telemetry():
    if os.path.exists('telemetry.json'):
        with open('telemetry.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    return jsonify({"error": "Telemetry not found"}), 404

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5005, debug=False)
