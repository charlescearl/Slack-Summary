from ts_summarizer import TextRankTsSummarizer
import requests
import json
from config import *
from ts_config import SUMMARY_INTERVALS
from slacker import Slacker
import slacker


class SlackRouter(object):
        def __init__(self,):
            self.slack = slacker.Slacker(keys["slack"])

        def get_response(self, channel_id):
            return self.slack.channels.history(channel_id)

        def get_summary(self, channel_id):
            response =  self.get_response(channel_id)
	    a = (response.body)
            summ = TextRankTsSummarizer(SUMMARY_INTERVALS)
            summary = summ.report_summary(a)
	    res = u"*Chat Summary:* \n " + summary + "\n \n"
            return res

