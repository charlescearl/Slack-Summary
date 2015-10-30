# -*- coding: utf-8 -*-
from collections import namedtuple
from datetime import (timedelta, datetime)
import re
import logging
import sys
import json
import io
from ts_config import TS_DEBUG, TS_LOG
import glob
from interval_summarizer import (IntervalSpec, TsSummarizer,
                                 canonicalize, ts_to_time, tagged_sum)
logging.basicConfig(level=logging.INFO)

class SpacyTsSummarizer(TsSummarizer):
    
    def __init__(self, ispecs):
        TsSummarizer.__init__(self, ispecs)
        log_level = logging.DEBUG if TS_DEBUG else logging.INFO
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh = logging.FileHandler(TS_LOG, mode='a', encoding='utf-8')
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        self.logger = logging.getLogger('sp_summarizer')
        self.logger.handlers = []
        self.logger.addHandler(fh)

    def set_summarizer(self, spacy_summ):
        self.sumr = spacy_summ
                
    def summarize_segment(self, msg_segment):
        """Return a summary of the text
        TODO: 1. Looks like spacy is not getting the main sentence from the message.
        2. Load times for the spacy summarizer won't cut it. Commenting out now 
           until this can be fixed
        """
        size, msgs, txt = msg_segment
        summ = txt + u' '
        can_dict = {canonicalize(msg['text']) : msg for msg in msgs if 'text' in msg}
        self.logger.info("Length of can_dict is %s", len(can_dict))
        simple_sum = tagged_sum(can_dict[max(can_dict.keys(), key=lambda x: len(x))]) 
        if len(msgs) < 10:
            #return the longest
            summ += simple_sum
        else:
            max_sents = {}
            for (txt, msg) in can_dict.items():
                if len(txt.split()) > 3:
                    sl = list(self.sumr.nlp(txt).sents)
                    max_sents[max(sl, key = lambda x: len(x)).text] = msg
            txt_sum = [v for v in self.sumr(u' '.join(max_sents.keys()), size)]
            self.logger.info("Canonical keys are \n%s", u' '.join(can_dict.keys()))
            self.logger.info("Spacy summ %s", txt_sum)
            nlp_summ = u'\n'.join([tagged_sum(max_sents[ss]) for ss in txt_sum if len(ss) > 1 and ss in max_sents])
            for ss in txt_sum:
                if ss not in max_sents and len(ss.split()) > 5:
                    self.logger.info("Searching for: %s", ss)
                    for (ky, msg) in max_sents.items():
                        if ss in ky or (len(ky.split()) > 10 and ky in ss):
                            nlp_summ += u'\n' + tagged_sum(msg)
            if len(nlp_summ) < 2:
                self.logger.info("Failed to find nlp summary using heuristic")
                summ += simple_sum
            else:
                summ += nlp_summ
        self.logger.info("Summary for segment %s is %s", msgs, summ) 
        return summ

    def parify_text(self, msg_segment):
        ptext = u'. '.join([SpacyTsSummarizer.flrg.sub(u'', msg['text']) for msg in msg_segment if 'text' in msg])
        self.logger.debug("Parified text is %s", ptext)
        return ptext

def main():
    asd = [{'minutes': 30, 'txt' : u'Summary for first 30 minutes:\n', 'size' : 2}, {'hours':36, 'txt' : u'Summary for next 36 hours:\n', 'size': 3}]
    logger = logging.getLogger(__name__)
    tr_summ = SpacyTsSummarizer(asd)
    all_msgs = []
    for msg_file in glob.glob('./data/*.json'):
        with io.open(msg_file, encoding='utf-8',) as mf:
            all_msgs += json.load(mf)
    logger.info(tr_summ.report_summary(all_msgs))
    
if __name__ == '__main__':
    main()
