# -*- coding: utf-8 -*-
from collections import namedtuple
from datetime import (timedelta, datetime)
import re
import logging
import sys
import json
import io
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class IntervalSpec(object):
    slk_ts = re.compile(r'(?P<epoch>[1-9][^\.]+).*')
    
    def __init__(self, seconds=0, minutes=0, hours=0, days=0, weeks=0, size=10):
        self.intv = timedelta(seconds=seconds, minutes=minutes, hours=hours, days=days, weeks=weeks)
        self.size = size

    def contains(self, ts_start, msg_ts):
        """
        Parameters
        start_ts : string in form EPOCH.ID start of interval
        msg_ts : string in form EPOCH.ID message
        Return
        boolean
        """
        return self.in_interval(ts_to_time(ts_start), ts_to_time(msg_ts))

    def in_interval(self, d0, d1):
        return d1 >= d0 and d1 <= d0 + self.intv 
    
class AbstractTsSummarizer(object):
    """Constructs summaries over a set of ranges"""
    def __init__(self, ispecs):
        self.intervals = map(lambda ispec: IntervalSpec(**ispec), ispecs)
        self.logger = logging.getLogger(__name__)

    def summarize(self, messages):
        """ Produce the input """
        return [self.summarize_segment(text_seg) for text_seg in self.segment_messages(messages)]

    def summarize_segment(self, text):
        """Call the summarizer that is used."""
        return text

    def segment_messages(self, messages):
        """Create message bins.
        Parameters
        messages : [ dict ] a list of messages
        Return
        [ [ dict ] ] a list of messages segmented
        """
        self.logger.debug("Running the segmenter")
        ts = None
        interval_idx = 0
        msg_intervals = []
        idx_start = 0
        idx_end = 0
        interval_start = None
        for (idx, msg) in enumerate(sorted(messages, key=lambda msg: ts_to_time(msg['ts']))):
            idx_end = idx
            self.logger.debug("Checking index %s message %s", idx, msg)
            if not interval_start:
                interval_start = msg['ts']
                self.logger.debug("Setting the initial interval to %s", interval_start)
            if interval_idx == len(self.intervals):
                self.logger.debug("Reached final interval now")
                self.logger.debug("Events at index %s message %s", idx, msg)
                break
            if not self.in_interval(interval_start, msg['ts'], interval_idx):
                self.logger.debug("Starting new interval at %s", msg['ts'])
                msg_intervals.append(messages[idx_start:idx_end])
                idx_start = idx
                interval_idx += 1
                interval_start = msg['ts']
            elif idx == len(messages) - 1:
                msg_intervals.append(messages[idx_start:idx_end+1])
        self.logger.debug("Computed intervals %s", msg_intervals)
        return msg_intervals

    def in_interval(self, istart, msg_ts, idx):
        """Check if the msg is inside the given interval
        Parmeters
        start_ts : string a Slack timestamp EPOCH.ID
        msg_ts : string a Slack timestamp EPOCH.ID
        Returns
        boolean
        """
        self.logger.debug("Checking to see if %s is between %s and end", msg_ts, istart)
        return self.intervals[idx].contains(istart, msg_ts)

def ts_to_time(slack_ts):
    """
    Parameters
    slack_ts : string EPOCH.ID
    Return
    datetime
    """
    return datetime.fromtimestamp(long(IntervalSpec.slk_ts.search(slack_ts).group('epoch')))

def main():
    test_msgs = json.load(io.open("./test-events.json", encoding='utf-8'))
    logger.debug("Loading msgs")
    asd = [{'minutes': 10}, {'hours':12}]
    summ = AbstractTsSummarizer(asd)
    msgs = summ.segment_messages(test_msgs)
    
if __name__ == '__main__':
    main()
