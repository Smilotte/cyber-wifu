from flask import Flask, request, Response
from flask_cors import CORS
import threading
from gpt.gpt_request import friend_chat, restart_sequence, start_sequence
from tts.tts_request import audio

app = Flask(__name__)
mutex = threading.Lock()
CORS(app, resources=r'/*')

prefix = "以下是我与一位名为木槿的Vtuber的对话，这位Vtuber创意丰富，聪明而又调皮可爱。"


@app.route('/chat')
def get_chat():
    global prefix
    text = request.args.get('text', '')
    prefix = prefix + restart_sequence + text + start_sequence
    response = friend_chat(prefix)
    threading.Thread(target=audio, kwargs={"response": response}).start()
    prefix = prefix + response
    print("prefix:\n" + prefix)
    return response


@app.route('/audio')
def get_audio():
    text = request.args.get('text', '')
    audio(text)
    return Response("200")


if __name__ == '__main__':
    app.run("0.0.0.0", 8080)
