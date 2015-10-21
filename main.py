from ts_summarizer import TextRankTsSummarizer
from flask import Flask, jsonify, request
import requests
from slacker import Slacker
import json
import os
from config import *
from ts_config import SUMMARY_INTERVALS
from slack_summary import SlackRouter

app = Flask(__name__)

@app.route("/slack", methods=['POST'])
def slackReq():
	req_data = request.form
        req = {
	        'channel_id' : req_data.getlist('channel_id'),
                'channel_name' : req_data['channel_name'],
                'user_id' : req_data['user_id'],
                'user_name' : req_data['user_name'],
                'params' : req_data['text']
                }
	return (SlackRouter().get_summary(**req))

if __name__ == "__main__":
	# Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
