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
import config

class SlackRouter(object):

        def __init__(self,):
            self.slack = slacker.Slacker(keys["slack"])
            log_level = logging.DEBUG if config.DEBUG else logging.INFO
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            fh = logging.FileHandler(config.LOG_FILE, mode='a', encoding='utf-8')
            fh.setLevel(log_level)
            fh.setFormatter(formatter)
            self.logger = logging.getLogger('slack_summary')
            self.logger.handlers = []
            self.logger.setLevel(log_level)
            self.logger.addHandler(fh)

        def get_response(self, channel_id):
            self.logger.debug(u'Generating summary for channel: %s', channel_id)
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
            self.logger.info(u'Summary request %s user_id: %s', request_id, user_id)
            self.logger.info(u'Summary request %s channel_name: %s', request_id, channel_name)
            self.logger.info(u'Summary request %s parameters: %s', request_id, params)
            self.logger.debug(u'Summary request %s messages: %s', request_id, a)
            self.logger.info(u'Summary request %s summary:\n %s', request_id, summary)
	    res = u"*Chat Summary:* \n " + summary + "\n \n"
            return res

