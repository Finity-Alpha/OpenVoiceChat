from flask import Flask, jsonify, request, g, render_template
from main import Chatbot
from preprompts import sales_pre_prompt, advisor_pre_prompt, call_pre_prompt
import torch

device = 'cuda' if torch.cuda.is_available() else 'cpu'

preprompt = advisor_pre_prompt

print('loading models...')
john = Chatbot(device=device)


app = Flask(__name__)

@app.before_request
def before_request():
    g.log = ''
    g.past_kv = None
    g.next_id = None



UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    g.log = ''
    g.past_kv = None
    g.next_id = None
    return render_template('chat.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    user_message = request.form['user_message']
    break_word = '[USER]'
    name = '[JOHN]'
    response, g.past_kv, g.next_id = john.generate_response_greedy(user_message, preprompt + g.log,
                                                               break_word, max_length=100, name=name,
                                                               past_key_vals=g.past_kv, next_id=g.next_id,
                                                               verbose=True, temp=0.6)
    response = response.replace('[USER]', '').replace('[END]', '').replace('[START]', '')
    return {'bot_response': response}


if __name__ == '__main__':
    app.run(debug=False)
