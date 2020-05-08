import textstat as textstat
from jira.client import JIRA
from pprint import pprint as print
import numpy as np
import nltk
import logging
import os, re


# Defines a function for connecting to Jira
def connect_jira(log, jira_server, jira_user, jira_password):
    '''
    Connect to JIRA. Return None on error
    '''
    try:
        log.info("Connecting to JIRA: %s" % jira_server)
        jira = JIRA(jira_server, basic_auth=(jira_user, jira_password))
        # ^--- Note the tuple
        return jira
    except Exception as e:
        log.error("Failed to connect to JIRA: %s" % e)
        return None

# Defines a function for scoring comments in Jira
def score_comment(text):
    #counters
    nouncount = 0

    #remove code but give points for it
    #search for {code} and add points here
    codecount = text.count('{code')
    text = re.sub(r'{code:(.|\r|\n)*{code}', '', text)

    #Check for link to PR
    linktopr = text.count('https://github.com')
    text = re.sub(r'https://github.com.*/pull', '', text)

    # Check for links to things
    linktothings = text.count('https://')
    text = re.sub(r'https?:\/\/.*[\r\n]*', '', text)

    # Count all sentences from all documents
    sentences = nltk.sent_tokenize(text)

    # tag speech
    tokens = nltk.word_tokenize(text)
    tagged_words = nltk.pos_tag(tokens)

    for type in tagged_words:
        if 'NN' in type[1]:
            nouncount += 1

    # Count Entities
    entities = nltk.chunk.ne_chunk(tagged_words, binary=True)
    named_entities = []

    for t in entities.subtrees():
        if t.label() == 'NE':
            named_entities.append(t)

    # Check Complexity of language grade level
    complexity = textstat.text_standard(text, float_output=True)

    score = len(named_entities)*10 + len(sentences)*2.5 + nouncount + codecount*5 + linktopr*10 + linktothings*5 + complexity

    #For cases where extra code and things add to the count
    if score > 100:
        return 100

    return score

def user_stats(dict):
    a = dict['comments']['score']

    dict['comments']['stats'] = {}
    dict['comments']['stats']['avarage'] = np.average(a)
    dict['comments']['stats']['max'] = {'value': np.max(a), 'body': dict['comments']['body'][a.index(np.max(a))]}
    dict['comments']['stats']['min'] = {'value': np.min(a), 'body': dict['comments']['body'][a.index(np.min(a))]}

    return

def main():
    teamscores = []
    # create logger
    log = logging.getLogger(__name__)

    username=os.getenv('USER')
    passwd=os.getenv('JIRAPW')

    # create a connection object, jc
    jc = connect_jira(log, 'https://issues.redhat.com', username, passwd)

    issues = jc.search_issues("project = WINC AND (sprint in openSprints())")

    usercomments = {}

    # format dict based on results from comments
    for result in issues:
        issue = jc.issue(result.id)
        comments = issue.fields.comment.comments
        for comment in comments:
            if comment.author.name not in usercomments:
                usercomments[comment.author.name] = {'comments': {'id': [], 'score': [], 'body':[], 'date': []}}
            usercomments[comment.author.name]['comments']['id'].insert(0, comment.id)
            usercomments[comment.author.name]['comments']['score'].insert(0, score_comment(comment.body))
            usercomments[comment.author.name]['comments']['body'].insert(0, comment.body)
            usercomments[comment.author.name]['comments']['date'].insert(0, comment.updated)

    for user in usercomments:
        user_stats(usercomments[user])
        teamscores.insert(0, [user, usercomments[user]['comments']['stats']['avarage']])

    print(sorted(teamscores, key=lambda x: x[1]))
    print(usercomments)

if __name__ == "__main__":
    main()
