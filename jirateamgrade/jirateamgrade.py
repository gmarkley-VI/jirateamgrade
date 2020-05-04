from jira.client import JIRA
from pprint import pprint as print
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

def main():
    # create logger
    log = logging.getLogger(__name__)

    username=os.getenv('USER')
    passwd=os.getenv('JIRAPW')

    # create a connection object, jc
    jc = connect_jira(log, 'https://issues.redhat.com', username, passwd)

    issue = jc.issue('SPLAT-8')
    print(issue.fields.description)

if __name__ == "__main__":
    main()
