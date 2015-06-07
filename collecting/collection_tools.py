import praw as pr
import time as tm
from sqlalchemy import MetaData, create_engine
from sqlalchemy.sql import select
import random

def subm_to_db(subm, conn, subm_table, com_table):
    values = {
            'submission_id' : subm.name,
            'title' : subm.title,
            'content' : subm.selftext,
            'timestamp' : int(tm.time()),
            'created' : int(subm.created),
            'score' : subm.score,
            'author' : str(subm.author),
            'num_comments' : subm.num_comments 
            }
    conn.execute(subm_table.insert(), [values])
    
    subm.replace_more_comments(limit=None, threshold=0)
    
    comments = pr.helpers.flatten_tree(subm.comments)
    
    for comment in comments:
        comment_to_db(comment, subm, conn, com_table)
                    

def comment_to_db(comment, subm, conn, table):
    values = {
            'comment_id' : comment.name,
            'user_id' : str(comment.author),
            'submission_id' : subm.name,
            'prev_comment_id' : comment.parent_id,
            'created' : int(comment.created),
            'timestamp' : int(tm.time()),
            'content' : comment.body,
            'subreddit' : comment.subreddit.title,
            'score' : comment.score
            }
           
    conn.execute(table.insert(), [values])
    
def run_once():
    
    subreddits = ['dataisbeautiful', 'programming', 'technology', 'python', 'cpp']
    engine = create_engine('mysql+pymysql://gautam@localhost/reddit_comments?charset=utf8')
    meta = MetaData()
    meta.reflect(bind=engine)
    comments = meta.tables['comments']
    submissions = meta.tables['submissions']
    conn = engine.connect()
    
    red = pr.Reddit(user_agent='creddit_score')
    subr = red.get_subreddit(subreddits[random.randint(0,len(subreddits)-1)])
    
    sub_already_there = True
    while sub_already_there:
        submission = subr.get_random_submission()
        s = select([submissions]).where(submissions.c.submission_id == submission.name)
        result = conn.execute(s).fetchall()
        sub_already_there = len(result) > 0
    subm_to_db(submission, conn, submissions, comments)
    print "added {} {}, {}".format(subr.name, submission.name, submission.num_comments)
    conn.close()

if __name__ == '__main__':
    run_once()

