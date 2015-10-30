# -*- coding: utf-8 -*-
from collections import namedtuple
from datetime import (timedelta, datetime)
import re
import logging
import sys
import json
import io
import lsa
import utils
import base_summarizer
import compat
from gensim.summarization import summarize as gs_sumrz
from gensim.models.word2vec import LineSentence
from ts_config import TS_DEBUG, TS_LOG
import glob
from interval_summarizer import (IntervalSpec, TsSummarizer,
                                 canonicalize, ts_to_time, tagged_sum)
logging.basicConfig(level=logging.INFO)

class TextRankTsSummarizer(TsSummarizer):
    #flrg = re.compile(r'[\n\r\.]|\&[a-z]+;|<http:[^>]+>|\:[^: ]+\:')
    #sumr = lsa.LsaSummarizer()
    
    def __init__(self, ispecs):
        TsSummarizer.__init__(self, ispecs)
        log_level = logging.DEBUG if TS_DEBUG else logging.INFO
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh = logging.FileHandler(TS_LOG, mode='a', encoding='utf-8')
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        self.logger = logging.getLogger('ts_summarizer')
        self.logger.handlers = []
        self.logger.addHandler(fh)

    def set_summarizer(self, val):
        pass
                
    def summarize_segment(self, msg_segment):
        """Return a summary of the text
        TODO: 1. Looks like spacy is not getting the main sentence from the message.
        2. Load times for the spacy summarizer won't cut it. Commenting out now 
           until this can be fixed
        """
        size, msgs, txt = msg_segment
        ratio = size / float(len(msgs))
        summ = txt + u' '
        can_dict = {canonicalize(msg['text']) : msg for msg in msgs if 'text' in msg}
        self.logger.info("Length of can_dict is %s", len(can_dict))
        simple_summ = tagged_sum(can_dict[max(can_dict.keys(), key=lambda x: len(x))])
        if len(msgs) < 10:
            #return the longest
            self.logger.warn("Too few messages for NLP.")
            summ += simple_summ
        else:
            #txt_sum = [v for v in TextRankTsSummarizer.sumr(u' '.join(can_dict.keys()), size)]
            #self.logger.info("Spacy summ %s", txt_sum)
            gn_sum = gs_sumrz(u' '.join(can_dict.keys()), ratio=ratio, split=True)[:size]
            self.logger.info("Gensim sum %s", gn_sum)
            #summ += u'\n'.join([tagged_sum(can_dict[ss]) for ss in gs_sumrz(u' '.join(can_dict.keys()), ratio=ratio, split=True)[:size] if len(ss) > 1])
            #summ += u'\n'.join([tagged_sum(can_dict[ss]) for ss in txt_sum if len(ss) > 1])
            gs_summ = u'\n'.join([tagged_sum(can_dict[ss]) for ss in gn_sum if len(ss) > 1])
            if len(gs_summ) > 5:
                summ += gs_summ
            else:
                self.logger.warn("NLP Summarizer produced null output %s", gs_summ)
                summ += simple_summ
        self.logger.info("Summary for segment %s is %s", msgs, summ) 
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
    return u'@{}  <{}>: {}'.format(ts_to_time(msg['ts']).strftime("%H:%M:%S %Z"), msg['user'],  msg['text'])

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
    logger = logging.getLogger(__name__)
    tr_summ = TextRankTsSummarizer(asd)
    all_msgs = []
    for msg_file in glob.glob('./data/*.json'):
        with io.open(msg_file, encoding='utf-8',) as mf:
            all_msgs += json.load(mf)
    logger.info(tr_summ.report_summary(all_msgs))
    
if __name__ == '__main__':
    main()
