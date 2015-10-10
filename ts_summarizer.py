# -*- coding: utf-8 -*-
from collections import namedtuple
from datetime import (timedelta, datetime)
import re
import logging
import sys
import json
import io
from gensim.summarization import summarize as gs_sumrz
from gensim.models.word2vec import LineSentence
from ts_config import TS_DEBUG
import glob

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntervalSpec(object):
    slk_ts = re.compile(r'(?P<epoch>[1-9][^\.]+).*')
    
    def __init__(self, seconds=0, minutes=0, hours=0, days=0, weeks=0, size=10, txt=u"Summary for interval: \n"):
        self.intv = timedelta(seconds=seconds, minutes=minutes, hours=hours, days=days, weeks=weeks)
        self.size = size
        self.txt = txt

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
        return d1 <= d0 and d1 >= d0 - self.intv 
    
class TsSummarizer(object):
    """Constructs summaries over a set of ranges"""
    def __init__(self, ispecs):
        self.intervals = map(lambda ispec: IntervalSpec(**ispec), ispecs)
        self.logger = logging.getLogger(__name__)

    def summarize(self, messages):
        """ Produce the input """
        return [self.summarize_segment(msg_seg) for msg_seg in self.segment_messages(messages)]

    def report_summary(self, messages):
        """The interval summaries are joined."""
        return '\n'.join(self.summarize(messages))

    def summarize_segment(self, msg_seg):
        """Call the summarizer that is used."""
        return msg_seg

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
        msgs = [msg for msg in messages if u'attachments' not in msg and u'text' in msg and u'subtype' not in msg]
        smessages = sorted(msgs, reverse=True, key=lambda msg: ts_to_time(msg['ts']))
        for (idx, msg) in enumerate(smessages):
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
                msg_intervals.append((self.intervals[interval_idx].size, smessages[idx_start:idx_end], self.intervals[interval_idx].txt))
                idx_start = idx
                interval_idx += 1
                interval_start = msg['ts']
            elif idx == len(messages) - 1:
                msg_intervals.append((self.intervals[interval_idx].size, smessages[idx_start:idx_end+1], self.intervals[interval_idx].txt))
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

class TextRankTsSummarizer(TsSummarizer):
    flrg = re.compile(r'[\n\r\.]|\&[a-z]+;|<http:[^>]+>')

    def __init__(self, ispecs):
        TsSummarizer.__init__(self, ispecs)
                
    def summarize_segment(self, msg_segment):
        """Return a summary of the text"""
        size, msgs, txt = msg_segment
        ratio = size / float(len(msgs))
        summ = txt + u' '
        can_dict = {canonicalize(msg['text']) : msg for msg in msgs if 'text' in msg}
        if len(msgs) < 10:
            #return the longest
            summ += tagged_sum(can_dict[max(can_dict.keys(), key=lambda x: len(x))])
        else:
            summ += u'\n'.join([tagged_sum(can_dict(ss)) for ss in gs_sumrz(u' '.join(can_dict.keys()), ratio=ratio).split('\n')])
        self.logger.debug("Summary for segment %s is %s", msgs, summ) 
        return summ

    def parify_text(self, msg_segment):
        ptext = u'. '.join([TextRankTsSummarizer.flrg.sub(u'', msg['text']) for msg in msg_segment if 'text' in msg])
        self.logger.debug("Parified text is %s", ptext)
        return ptext

def canonicalize(txt):
    """Filter and change text to sentece form"""
    ntxt = TextRankTsSummarizer.flrg.sub(u'', txt)
    return ntxt if re.match(r'.*[\.\?]$', ntxt) else u'{}.'.format(ntxt)

def tagged_sum(msg):
    return u'USER:{} at {}: {}'.format(msg['user'], msg['ts'], msg['text'])

def ts_to_time(slack_ts):
    """
    Parameters
    slack_ts : string EPOCH.ID
    Return
    datetime
    """
    return datetime.fromtimestamp(long(IntervalSpec.slk_ts.search(slack_ts).group('epoch')))

def main():
    asd = [{'minutes': 30, 'txt' : u'Summary for first 30 minutes:\n', 'size' : 2}, {'hours':36, 'txt' : u'Summary for next 36 hours:\n', 'size': 3}]
    # test_msgs = json.load(io.open("./test-events.json", encoding='utf-8'))
    # logger.debug("Loading msgs")
    # summ = TsSummarizer(asd)
    # msgs = summ.segment_messages(test_msgs)
    tr_summ = TextRankTsSummarizer(asd)
    all_msgs = []
    for msg_file in glob.glob('/Users/gayatrisethi/Documents/wp_summarizer/nosara/*.json'):
        with io.open(msg_file, encoding='utf-8',) as mf:
            all_msgs += json.load(mf)
    logger.info(tr_summ.report_summary(all_msgs))
    
if __name__ == '__main__':
    main()
