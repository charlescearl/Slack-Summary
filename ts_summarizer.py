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
        if len(msgs) == 0:
            self.logger.warn("No messages to form summary")
            return u"\n Unable to form summary here.\n"
        ratio = size / float(len(msgs))
        summ = txt + u' '
        can_dict = {canonicalize(msg['text']) : msg for msg in msgs if 'text' in msg}
        self.logger.info("Length of can_dict is %s", len(can_dict))
        simple_summ = tagged_sum(can_dict[max(can_dict.keys(), key=lambda x: len(x))])
        # If the number of messages or vocabulary is too low, just look for a
        # promising set of messages
        if len(msgs) < 11 or ratio == 0 or len(can_dict) < 11:
            #return the longest
            self.logger.warn("Too few messages for NLP.")
            summ += simple_summ
        else:
            max_sents = {}
            for (txt, msg) in can_dict.items():
                if len(txt.split()) > 3:
                    sl = txt.split('. ')
                    max_sents[max(sl, key = lambda x: len(x))] = msg
            self.logger.info("Ratio: %s, Length of keys: %s, %s", ratio, len(can_dict.keys()), len(max_sents.keys()))
            gn_sum = gs_sumrz(u'. '.join(can_dict.keys()), ratio=ratio, split=True)[:size]
            mx_sum = gs_sumrz(u'. '.join(max_sents.keys()), ratio=ratio, split=True)[:size]
            self.logger.info("Gensim sum %s", gn_sum)
            gs_summ = u'\n'.join([tagged_sum(can_dict[ss]) for ss in gn_sum if len(ss) > 1 and ss in max_sents])
            for ss in mx_sum:
                if ss not in max_sents and len(ss.split()) > 5:
                    self.logger.info("Searching for: %s", ss)
                    for (ky, msg) in max_sents.items():
                        if ss in ky or (len(ky.split()) > 10 and ky in ss):
                            gs_summ += u'\n' + tagged_sum(msg)
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
