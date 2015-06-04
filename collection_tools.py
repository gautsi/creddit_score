import praw as pr
import time as tm
from sqlalchemy import MetaData, create_engine
from sqlalchemy.sql import select

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
        comment_to_db(comment, conn, com_table)
                    

def comment_to_db(comment, conn, table):
    values = {
            'comment_id' : comment.name,
            'user_id' : str(comment.author),
            'submission_id' : submission.id,
            'prev_comment_id' : comment.parent_id,
            'created' : int(comment.created),
            'timestamp' : int(tm.time()),
            'content' : comment.body,
            'subreddit' : comment.subreddit.title,
            'score' : comment.score
            }
           
    conn.execute(table.insert(), [values])

if __name__ == '__main__':
    engine = create_engine('mysql+pymysql://root:tattwamasi@localhost/reddit_comments')
    meta = MetaData()
    meta.reflect(bind=engine)
    comments = meta.tables['comments']
    submissions = meta.tables['submissions']
    conn = engine.connect()
    
    red = pr.Reddit(user_agent='creddit_score')
    funny = red.get_subreddit('funny')
    
    sub_already_there = True
    while sub_already_there:
        submission = funny.get_random_submission()
        s = select([submissions]).where(submissions.c.submission_id == submission.name)
        result = conn.execute(s).fetchall()
        sub_already_there = len(result) > 0
    subm_to_db(submission, conn, submissions, comments)
    print "added {}, {}".format(submission.title, submission.num_comments)
    conn.close()

