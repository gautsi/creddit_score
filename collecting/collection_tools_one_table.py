import praw as pr
import time as tm
from sqlalchemy import MetaData, create_engine
from sqlalchemy.sql import select
import random
from sqlalchemy.exc import StatementError

def subm_to_db(subm, conn, subm_table, com_table):
    
    subm_table_values = {
                         'submission_id' : subm.name,
                         'subreddit' : subm.subreddit.title,
                         'timestamp' : int(tm.time())
                         }

    conn.execute(subm_table.insert(), [subm_table_values])
    
    subm_values = {
                   'submission_id' : subm.name,
                   'subm_title' : subm.title,
                   'subm_content' : subm.selftext,
                   'subm_created' : int(subm.created_utc),
                   'subm_created_local' : int(subm.created),
                   'subm_score' : subm.score,
                   'subm_author' : str(subm.author),
                   'subm_num_comments' : subm.num_comments 
            }
   
    subm.replace_more_comments(limit=None, threshold=0)
    
    comments = pr.helpers.flatten_tree(subm.comments)
    
    for comment in comments:
        comment_to_db(comment, subm_values, conn, com_table)
                    

def comment_to_db(comment, subm_values, conn, table):
    values = {
              'comment_id' : comment.name,
              'user_id' : str(comment.author),
              'prev_comment_id' : comment.parent_id,
              'created' : int(comment.created_utc),
              'created_local' : int(comment.created),
              'timestamp' : int(tm.time()),
              'content' : comment.body,
              'subreddit' : comment.subreddit.title,
              'score' : comment.score,
              'ups' : comment.ups,
              'downs' : comment.downs,
              'controversiality' : comment.controversiality
            }
    values.update(subm_values)
    try:
        conn.execute(table.insert(), [values])
    except (UnicodeEncodeError, StatementError):
        print "unicode error at comment level"
        pass


def run_once():
    
    subreddits = ['dataisbeautiful', 'programming', 'technology', 'python', 'cpp', 'funny', 'news', 'science']
    
    engine = create_engine('mysql+pymysql://gautam@localhost/reddit_comments_submissions')
    meta = MetaData()
    meta.reflect(bind=engine)
    comm_subm = meta.tables['comm_subm']
    submissions = meta.tables['submissions']
    conn = engine.connect()
    
    red = pr.Reddit(user_agent='creddit_score')
    
    sub_already_there = True
    while sub_already_there:
        subr = red.get_subreddit(subreddits[random.randint(0,len(subreddits)-1)])
        submission = subr.get_random_submission()
        s = select([submissions]).where(submissions.c.submission_id == submission.name)
        result = conn.execute(s).fetchall()
        sub_already_there = len(result) > 0
        if sub_already_there:
            if tm.time() - submission.created_utc < 120000\
            and not result[0]['timestamp'] is None\
            and tm.time() - max([row['timestamp'] for row in result]) > 600\
            and submission.num_comments > 10:
                sub_already_there = False
                print "sub already here add {} in {}".format(submission.name, subr.title)
            else:
                print "sub already here ignore {} in {}".format(submission.name, subr.title)
    
    subm_to_db(submission, conn, submissions, comm_subm)

    print "added {} {}, {}".format(subr.title, submission.name, submission.num_comments)
    conn.close()
    
if __name__ == '__main__':
    run_once()
