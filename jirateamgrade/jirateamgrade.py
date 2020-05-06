from jira.client import JIRA
from pprint import pprint as print
import numpy as np
import nltk
import logging
import os


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
def scoreComment(text):
    #counters
    noun = 0
    verb = 0

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

    score = len(named_entities)*10 + len(sentences)*2.5 + noun + verb

    return score

def main():
    # create logger
    log = logging.getLogger(__name__)

    username=os.getenv('USER')
    passwd=os.getenv('JIRAPW')

    # create a connection object, jc
    jc = connect_jira(log, 'https://issues.redhat.com', username, passwd)

    issues = jc.search_issues("project = WINC AND (sprint in openSprints()) AND assignee in (rgudimet)")

    usercomments = {}

    for result in issues:
        issue = jc.issue(result.id)
        comments = issue.fields.comment.comments
        for comment in comments:
            if comment.author.name not in usercomments:
                usercomments[comment.author.name] = {'comments': {'id': [], 'score': [], 'body':[]}}
            usercomments[comment.author.name]['comments']['id'].insert(0, comment.id)
            usercomments[comment.author.name]['comments']['score'].insert(0, scoreComment(comment.body))
            usercomments[comment.author.name]['comments']['body'].insert(0, comment.body)

    print(usercomments)

    # for key in usercomments:
    #     scores = usercomments[key]['score']
    #     print(key)
    #     print(np.max(scores))
    #     print(np.average(scores))
    #     print(np.min(scores))


    #print(usercomments)

            #grade.append([comment.author.displayName, scoreComment(comment.body)])

if __name__ == "__main__":
    main()
