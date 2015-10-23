# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from collections import namedtuple
from operator import attrgetter
from utils import ItemsCount
import logging
logging.basicConfig(level=logging.INFO)

SentenceInfo = namedtuple("SentenceInfo", ("sentence", "order", "rating",))

class BaseSummarizer(object):
    def __init__(self, ):
        self.logger = logging.getLogger(__name__)
        
    def __call__(self, document, sentences_count):
        raise NotImplementedError("This method should be overriden in subclass")

    def normalize_word(self, word):
        return word.lower()

    def _get_best_sentences(self, sentences, count, rating, *args, **kwargs):
        rate = rating
        self.logger.info("Sentences are %s" % sentences)
        #rate = lambda s: rating[s]
        # if isinstance(rating, dict):
        #     assert not args and not kwargs
        #     rate = lambda s: rating[s]

        infos = (SentenceInfo(s, o, rate(s, *args, **kwargs))
            for o, s in enumerate(sentences))

        # sort sentences by rating in descending order
        infos = sorted(infos, key=attrgetter("rating"), reverse=True)
        # get `count` first best rated sentences
        count = ItemsCount(count)
        # if not isinstance(count, ItemsCount):
        #     count = ItemsCount(count)
        infos = count(infos)
        # sort sentences by their order in document
        infos = sorted(infos, key=attrgetter("order"))

        return tuple(i.sentence for i in infos)
