import matplotlib.pyplot as plt
import matplotlib.colors as cl
import matplotlib.cm as cm
import numpy as np
import pandas as pd
from sqlalchemy import MetaData, create_engine
from sqlalchemy.sql import select
from sqlalchemy.exc import StatementError
import praw as pr
import time as tm
import random

#Make a praw object
red = pr.Reddit(user_agent='creddit_score')

#Define subreddits
subreddits = ['DataIsBeautiful', 'programming', 'Technology', 'Python', 'C++']

#Connect to database 
engine = create_engine('mysql+pymysql://root:tattwamasi@localhost/reddit_comments_submissions')
meta = MetaData()
meta.reflect(bind=engine)
comm_subm = meta.tables['comm_subm']
submissions = meta.tables['submissions']
conn = engine.connect()

#Make dataframes
comments_df = pd.read_sql(sql="select * from comm_subm limit 10000", con=engine)
#submissions_df = pd.read_sql(sql="select * from submissions", con=engine)

#Add features
comments_df['age'] = comments_df.created - comments_df.subm_created
comments_df['age_min'] = comments_df.age/60.0
comments_df['age_min_log'] = np.log10(comments_df.age_min)
comments_df['time_since_post'] = comments_df.timestamp - comments_df.created
comments_df['time_since_post_min'] = comments_df.time_since_post/60.0
comments_df['time_since_post_min_log'] = np.log10(comments_df.time_since_post_min)
comments_df['color'] = comments_df.subreddit.apply(lambda x : subreddits.index(x))
comments_df['comment_length'] = comments_df.content.apply(len)
comments_df['comment_num_words'] = comments_df.content.apply(lambda x : len(x.split()))
comments_df['comment_length_log'] = np.log10(comments_df.comment_length)
comments_df['comment_num_words_log'] = np.log10(comments_df.comment_num_words)
comments_df['subm_num_comments_log'] = np.log10(comments_df.subm_num_comments)



