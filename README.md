# Slack Summary

Summarize it is a chat summarizer plugin for instant messaging applications. It summarizes the large content of chat logs which enables users to quickly understand the current context of the conversation. Currently Summarize it works on top of Slack as its plugin.

The original relied on an HP cloud concepts expraction api. We've pulled that out to remove any reliance on 3rd party apis, and are going to improve the summarizations.

## Installing Summarize It plugin for your slack

To install the summary package

Firsts, create a token for your team `https://api.slack.com/web` 

   	   pip install flask requests slacker wsgiref jupyter mock pbr spacy numpy

Then run

     python -m spacy.en.download all

Edit the `config.py` file that it includes the line

     keys = {
     	     "slack": "your-token-here"
    	     }

Then edit `ts_config.py` file to adjust the debugging options

     SUMMARY_INTERVALS = [{'minutes': 10, 'size': 1}, {'hours':12, 'size': 2}]
     TS_DEBUG = True
     TS_LOG = "./ts_summ.log"
     DEBUG=True
     LOG_FILE="./summary.log"

Here the `LOG_FILE` stores where notices of users accessing the server is stored and the
value of `DEBUG` determines if detailed logging is stored.

The plugin is executed by running

    python main.py


Tests are currently setup to run in a python `virtualenv`. These will executed by
runnning

	make check

but realize that the <b>test will install and run in a virtualenv</b>


To complete the installation

1. Visit `https://<your-team-name>.slack.com/services/new/slash-commands`

2. Enter the command name you wish to use

3. Enter the request url as `<your-deployed-app-url>/slack`

## Using Summarize It plugin with slack
Type /your-command to initiate the plugin. The plugin will automatically summarize the above chat contents and display the summary.

## Screenshots

#### Hackathon Discussion
![Hackathon Discussion](img/hackathon-discussion.png)

#### Meeting Discussion
![Meeting Discussion](img/meeting-discussion.png)

## Authors and Contributors
Yask Srivastava (Developer), [Ketan Bhatt](https://github.com/ketanbhatt) (Developer), [Pranu Sarna](https://github.com/psarna94) (Developer) and [Vinayak Mehta](https://github.com/vortex-ape) (Data Scientist).

## Support or Contact
Having trouble with summarize it? Create an issue in the repository GitHub Repo.

