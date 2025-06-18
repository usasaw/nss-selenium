# from flask import Flask, render_template, jsonify
# from src.browser_test.true_move import run_test
import eventlet
eventlet.monkey_patch()

import os
import base64
import glob
import time

from flask import Flask, render_template, jsonify, request  # ← request มาจาก flask
from flask_socketio import SocketIO, emit
from src.browser_test.true_move import run_test
from src.constants.data import cards

app = Flask(__name__)
# socketio = SocketIO(app)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route("/")
def index():
   return render_template("index.html")

@app.route("/api/cards")
def get_cards():
   return jsonify(cards)

@socketio.on("start_test")
def handle_run_test(CS_CODE):
   sid = request.sid
   clear_old_screenshots(CS_CODE)              # 🔁 เคลียร์ภาพของ CS_CODE นี้เท่านั้น
   run_test(socketio, sid, CS_CODE)            # ▶️ รันเทส
   send_screenshots(socketio, sid, CS_CODE)    # 🖼️ ส่งภาพของ CS_CODE นี้

def clear_old_screenshots(CS_CODE, base_folder="screenshots"):
   folder = os.path.join(base_folder, str(CS_CODE))
   if os.path.exists(folder):
      for f in glob.glob(os.path.join(folder, "*.png")):
         os.remove(f)

def send_screenshots(socketio, sid, CS_CODE, base_folder="screenshots"):
   folder = os.path.join(base_folder, str(CS_CODE))
   if not os.path.exists(folder):
      return

   sent = set()
   for filepath in sorted(glob.glob(os.path.join(folder, "*.png"))):
      if filepath not in sent:
         with open(filepath, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode('utf-8')
         filename = os.path.basename(filepath)
         socketio.emit('screenshot', {'base64': encoded, 'filename': filename}, to=sid)
         sent.add(filepath)

if __name__ == "__main__":
   socketio.run(app, debug=True)
