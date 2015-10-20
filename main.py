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
	channel_id = req_data.getlist('channel_id')
	return (SlackRouter().get_summary(channel_id))

if __name__ == "__main__":
	# Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
