import unittest
import json
import io
from ts_summarizer import (IntervalSpec, AbstractTsSummarizer,
                           ts_to_time)
from datetime import datetime
import logging
import sys

logger = logging.getLogger()
logger.level = logging.DEBUG

class TestSummarize(unittest.TestCase):
    
    def test_interval_conversion(self):
        self.assertTrue(ts_to_time("1441925382.000186") == datetime.fromtimestamp(1441925382))

    def test_create_intervals(self):
        test_msgs = json.load(io.open("./test-events.json", encoding='utf-8'))
        asd = [{'minutes': 10}, {'hours':12}]
        self.assertTrue(len(test_msgs) == 8)
        summ = AbstractTsSummarizer(asd)
        msgs = summ.segment_messages(test_msgs)
        logger.debug("Messages received %s", msgs)
        self.assertTrue(len(msgs) == 2)
        logger.debug("First entry should be %s is %s", test_msgs[0:4], msgs[0])
        self.assertTrue(msgs[0] == test_msgs[0:4])
        self.assertTrue(msgs[1] == test_msgs[4:])
        asd2 = [{'minutes': 5}, ]
        summ = AbstractTsSummarizer(asd2)
        msgs = summ.segment_messages(test_msgs)
        logger.debug("Messages received %s", msgs)
        self.assertTrue(len(msgs) == 1)
        logger.debug("First entry should be %s is %s", test_msgs[0:4], msgs[0])
        self.assertTrue(msgs[0] == test_msgs[0:4])

    def test_text_rank_summarization(self):
        """Pass the intervals to Gensim TextRank"""
        pass

    def test_service_ingest(self):
        """Stand up the endpoint, send some events via requests"""
        pass

if __name__ == '__main__':
    unittest.main()

