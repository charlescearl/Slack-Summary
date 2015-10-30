from flask import Flask, jsonify, request
import requests
import json
import os
from config import *
from slack_summary import SlackRouter
import lsa
import spacy.en
import spacy
from util
app = Flask(__name__)
global summ
global np 
summ = lsa.LsaSummarizer()
nlp = spacy.en.English()


@app.route("/slack", methods=['POST'])
def slackReq():
        global summ
        if not summ:
                summ = lsa.LsaSummarizer()
	req_data = request.form
        req = {
	        'channel_id' : req_data.getlist('channel_id'),
                'channel_name' : req_data['channel_name'],
                'user_id' : req_data['user_id'],
                'user_name' : req_data['user_name'],
                'params' : req_data['text'],
                'summ' : summ
                }
	return (SlackRouter().get_summary(**req))


@app.route("/slacktest", methods=['POST'])
def slackTestReq():
        global summ
        if not summ:
                summ = lsa.LsaSummarizer()
	req_data = request.form
        req = {
	        'channel_id' : req_data.getlist('channel_id'),
                'channel_name' : req_data['channel_name'],
                'user_id' : req_data['user_id'],
                'user_name' : req_data['user_name'],
                'params' : req_data['text'],
                'summ' : summ,
                'test' : True
                }
	return (SlackRouter(test=True).get_summary(**req))
        #return u' '.join([nc, for nc in nlp(u'This is to be parsed')])

def main():
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=False)
        
if __name__ == "__main__":
        main()
