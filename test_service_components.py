import logging
import unittest
from mock import MagicMock, patch
import mock
from slacker import Slacker
import slacker
import main
from slack_summary import SlackRouter
from requests import Response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Test(unittest.TestCase):
    def setUp(self):
        self.expected = [{u'text': u'hmmm...',
                       u'ts': u'1414028037.000317',
                       u'type': u'message',
                       u'user': u'U027LSDDA'}]
        self.myresponse = Response()
        self.myresponse.body = self.expected
        self.myresponse.status_code = 200
        attrs = {'history.return_value': self.myresponse,}
        self.channel_mock = MagicMock(**attrs)
        main.app.config['TESTING'] = True
        self.app = main.app.test_client()

    def tearDown(self):
        pass
    
    @mock.patch('slacker.Slacker')
    def test_summary(self, mock_slack):
        mock_slack.return_value.channels = self.channel_mock
        sr = SlackRouter()
        self.assertTrue(sr.get_response('achannell') == self.myresponse)

    @mock.patch('slacker.Slacker')
    def test_service(self, mock_slack):
        mock_slack.return_value.channels = self.channel_mock
        rv = self.app.post('/slack', data=dict(
                    channel_id='achannel',
                    channel_name='achannel',
                    user_id='user123',
                    user_name='bob',
                    text='-5 days @bob'
                ), follow_redirects=True)
        logger.info("Response is %s", rv.data)
        self.assertTrue(rv.status_code == 200)
        

if __name__ == '__main__':
    unittest.main()
