A basic Slack chat summarizer has been developed for public Slack channels. It can be invoked at
the Slack application prompt by typing the command `/summary`

The summarizer application takes as input a look-back time window on which to construct the summary. For example

<code>
       /summary -5 days
       </code>

generates a summary that includes messages from five days ago up to
the present time.

The `command` syntax formally is

	<command> ::= /summary -<time-units-back> <time-unit>
        <time-unit> ::= minutes|hours|days|weeks
        <time-units-back> ::= integer

so

	/summary -5 hours
        /summary -30 minutes

means "generate a summary covering the last 5 hours" and "generate a summary covering the last 30 minutes" respectively.

I was aware generally of the approaches to Natural Language Processing (NLP) based summarization
prior to this exercise but
had not developed applications based on this technology. Summarization
algorithms can be roughly divided into two classes: those that select the most
informative sentence or sentences from a text and present this
subset as the summarization (the <bold>extractive</bold> approach);
and those which attempt to construct new text to paraphrase the
document (the <bold>abstractive</bold> approach). The abstractive methods rely
either upon a large collection of labeled examples (an article to a
title or article to an abstract) giving the program lots of
curated examples to learn from, or upon an extensive set of
specialized summarization templates. [A recent paper by Facebook research](http://arxiv.org/pdf/1509.00685v2.pdf "Facebook
Summarization Paper") gives a sampling of the state of the art
here. For my trial, labeled examples were not available and
developing a comprehensive set of  templates would have required an
extensive development effort. I therefore began by looking at extractive methods.

I looked closely at two Python  APIs for
extractive summarization. The summarizer provided by [the Gensim Python library](http://radimrehurek.com/gensim/) constructs a graph of the
sentences (messages more precisely) and picks the subset of messages most centrally located in
terms of the words (tokens) used in all messages -- this is based on pagerank and
implements an [algorithm named Textrank](https://web.eecs.umich.edu/~mihalcea/papers/mihalcea.emnlp04.pdf). The
other  approach takes the set of messages and forms a [latent topic space](http://www.cs.bham.ac.uk/~pxt/IDA/text_summary.pdf) -- it
essentially determines clusters of co-occuring words -- and ranks
each message in terms of its inclusion of tokens from each of the clusters. The
latter approach looked better based upon "eyeballing" and in more
extensive testing was more performant (the graph approach ground to a
halt when the number of messages got over 300).

Both summarizers assume
that the documents to be summarized are articles as opposed to chat
messages -- that is there are structural regularities that can be
exploited to improve summarization. First, many of the Slack dialogs
center around topics first introduced by questions or
requests that provide a fair amount of detail (e.g. "I'd like to..."
do something with elasticsearch, "Could we" implement a particular feature, "Would someone
help me with..." a tracks issue). I developed filters that search for the noun and verb
phrases associated with those requests using keywords as a guide. I then looked for proper
noun phrases -- working under the assumption that the frequency based
scoring done by the summarizer would link the important concepts of
the conversation. For chat sessions, the user posting the message is
also an important token and my cluster model accounts for clusters
built around the users posting to a channel. I also did some minimal
accounting for robot postings.

It also happened that the [spaCy NLP library](https://spacy.io/)
was just made open source as the trial began. The Spacy library now constitutes the
state of the art in terms of NLP capability in Python, and inclusion of this API
enabled performant extraction of part of speech tags.

We faced and resolved some challenges in getting the summarizer deployed. Greg
uncovered and resolved some issues with deploying spacy in the A8c
server environment. We discovered that more memory was needed for
deployment beyond that in the default environment. Trying to recreate
the essential characteristics of the Slack API interactions without
full access to the Slack channels was another challenge. Here, mocks and
specification-based testing proved vital to identifying
and fixing edge case bugs in the code.

In particular, I found specification based testing approach
invaluable, using the
[Hypothesis specification-based testing library](https://hypothesis.readthedocs.org/en/master/). I could
specify that the summaries were to be tested on a collection of Slack
channel logs (using test sets assembled by Greg) and have the Hypothesis framework randomly pick a range of summary windows, summary
sizes, and channels. Using this
specification of input domain, the Hypothesis test generator performed an iterative search of the example space
guided by results of previous test. This enabled me to test the summarizers on thousands of examples
before running the summarizer live.

Ideally the summarizer would score the relevance of a sentence
based upon a global (across the complete history of the channel)
notion of topics rather than exclusively over the summarization window
(e.g. 2 hours). Martin has pointed out a bias to pronouns (likely the
effect of including the question templates) and for messages having
links to other Slack messages. This may well be due also to
the heuristic of looking for the longest set of messages when the
sample size for the algorithm falls below minimum message and message
length threshold. Earlier on in the trial, I ran a topic analysis of
select channels, pulling out clusters of terms using [LDA](https://en.wikipedia.org/wiki/Latent_Dirichlet_allocation). The globally extracted
topics could be combined with the local window model to pull out the
most interesting messages. My reason for not doing this was the time constraint -- it would have involved running an update loop
over all channels and then storing the models. Easy enough to do in
principle but would have required additional memory and might have
raised other infrastructure issues to debug.

In the final weeks of the project, most of the interaction with the
team was in Slack or through Github pull requests. This was mostly due
a result of wanting to rapidly iterate on the summarizer to get a
working system out.

Overall the trial was exciting. I had a chance to do some debugging
with Greg, discovered in hypothesis a useful tool for scalability
testing, put the spacy library through its paces uncovering some bugs,
and insights into text summarization that could inform a larger
project.
