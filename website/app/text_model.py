import numpy as np
import pandas as pd
from sqlalchemy import MetaData, create_engine
from sklearn import linear_model, cross_validation
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from textblob import TextBlob
import pickle

engine = create_engine('mysql+pymysql://gautam@localhost/reddit_comments_submissions')

classes = {'bad' : 0, 'neutral' : 1, 'good' : 2}

low_thresh = 0
high_thresh = 15



def normalize(X):
    mean = X.mean()
    range_X = X.max() - X.min()
    return (X - mean)/float(range_X), mean, range_X

def denorm(norm, mean, range_X):
    return mean + norm*range_X

def cube_root(x):
    if x > 0:
        return x**(1.0/3.0)
    else:
        return -1*(-1*x)**(1.0/3.0)
    
def add_features(df):
    df['age'] = df.created - df.subm_created
    df['age_min'] = df.age/60.0
    df['age_min_log'] = np.log10(df.age_min)
    df['time_since_post'] = df.timestamp - df.created
    df['time_since_post_min'] = df.time_since_post/60.0
    df['time_since_post_min_log'] = np.log10(df.time_since_post_min)
    #df['color'] = df.subreddit.apply(lambda x : cs.subreddits.index(x))
    df['comment_length'] = df.content.apply(len)
    df['comment_num_words'] = df.content.apply(lambda x : len(x.split()))
    df['comment_length_log'] = np.log10(df.comment_length)
    df['comment_num_words_log'] = np.log10(df.comment_num_words)
    df['subm_num_comments_log'] = np.log10(df.subm_num_comments)
    #df['poor'] = df.score.apply(lambda x : -1 if x < thresh else 1)
    df['cube_score'] = df.score.apply(lambda x : cube_root(x))
    df['cube_subm_score'] = df.subm_score.apply(lambda x : cube_root(x))
    df['cls'] = df.score.apply(lambda x : 'bad' if x < 0 else ('good' if x > 15 else 'neutral'))
    df['cls_color'] = df.cls.apply(lambda x: classes[x])
    df['polarity'] = df.content.apply(lambda x : TextBlob(x).polarity)
    df['subjectivity'] = df.content.apply(lambda x : TextBlob(x).subjectivity)
    
    

dib_df = pd.read_sql(sql="select *\
                     from comm_subm\
                     where subreddit='DataIsBeautiful'",                    
                     con=engine)

comments_most_recent = dib_df.groupby(dib_df.comment_id).last()

comments_most_recent['cls'] = comments_most_recent.score.apply(lambda x : 'bad' if x < 0 else ('good' if x > 15 else 'neutral'))

good_df = comments_most_recent[comments_most_recent.cls == 'good']
bad_df = comments_most_recent[comments_most_recent.cls == 'bad']

good_bad_df = pd.concat([good_df, bad_df])

text_mnb = Pipeline([('vect', CountVectorizer(ngram_range = (1,4), stop_words='english', max_features=1000)),
                    ('tfidf', TfidfTransformer(use_idf=False)),
                     ('gnb', MultinomialNB()),
                     ])

text_mnb.fit(good_bad_df.content, good_bad_df.cls)

write_file = open('text_mnb_first_dump', 'w')
pickle.dump(text_mnb, write_file)


