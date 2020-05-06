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
    noun = 0
    verb = 0
    codecount = 0

    #remove code but give points for it
    #search for {code} and add points here
    if re.search(r'{code}', text):
        text = re.sub(r'{code:(.|\r|\n)*{code}', '', text)
        codecount = text.count('{code')

    # Count all sentences from all documents
    sentences = nltk.sent_tokenize(text)

    # tag speech
    tokens = nltk.word_tokenize(text)
    tagged_words = nltk.pos_tag(tokens)

    for type in tagged_words:
        if 'NN' in type[1]:
            noun += 1
        if 'VB' in type[1]:
            verb += 1

    # Count Entities
    entities = nltk.chunk.ne_chunk(tagged_words, binary=True)
    named_entities = []

    for t in entities.subtrees():
        if t.label() == 'NE':
            named_entities.append(t)

    score = len(named_entities)*10 + len(sentences)*2.5 + noun + verb +codecount*5

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
        print(user)
        print(usercomments[user]['comments']['stats'])

    #print(usercomments)

if __name__ == "__main__":
    main()
