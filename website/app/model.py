import numpy as np
import pandas as pd
from sqlalchemy import MetaData, create_engine
from sklearn import linear_model, cross_validation
import praw as pr


red = pr.Reddit(user_agent='creddit_score')

engine = create_engine('mysql+pymysql://gautam@localhost/reddit_comments_submissions')

comments_df = pd.read_sql(sql="select * from comm_subm limit 10000", con=engine)

comments_df['age'] = comments_df.created - comments_df.subm_created
comments_df['comment_length'] = comments_df.content.apply(len)

model = linear_model.LinearRegression()

features = ['subm_score', 'subm_num_comments', 'age', 'comment_length']

data_set = comments_df[features]

X_train, X_test, y_train, y_test = cross_validation.train_test_split(comments_df[features], comments_df.score, test_size=0.4, random_state=0)

model.fit(X=X_train, y=y_train)
