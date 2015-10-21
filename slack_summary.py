# -*- coding: utf-8 -*-
from ts_summarizer import TextRankTsSummarizer
import requests
import json
from config import *
from ts_config import SUMMARY_INTERVALS
from slacker import Slacker
import slacker
import logging
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SlackRouter(object):
        def __init__(self,):
            self.slack = slacker.Slacker(keys["slack"])

        def get_response(self, channel_id):
            logger.info(u'Generating summary for channel: %s', channel_id)
            return self.slack.channels.history(channel_id)

        def get_summary(self, **args):
            channel_id = args['channel_id']
            channel_name = args['channel_name']
            user_id = args['user_id']
            user_name = args['user_name']
            params = args['params']
            request_id = uuid.uuid1()
            response =  self.get_response(channel_id)
	    a = (response.body)
            summ = TextRankTsSummarizer(SUMMARY_INTERVALS)
            summary = summ.report_summary(a)
            logger.info(u'Summary request %s user_id: %s', request_id, user_id)
            logger.info(u'Summary request %s channel_name: %s', request_id, channel_name)
            logger.info(u'Summary request %s parameters: %s', request_id, params)
            logger.info(u'Summary request %s summary:\n %s', request_id, summary)
	    res = u"*Chat Summary:* \n " + summary + "\n \n"
            return res

