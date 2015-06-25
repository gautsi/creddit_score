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

classes = {'bad' : 0, 'neutral' : 1, 'good' : 2}
colors = ['#d95f02', 'b', '#756bb1']
lcm = cl.ListedColormap(colors)

#colors:
#light orange fc8d62
#violet 8da0cb
#dark orange d95f02
#dark green 1b9e77
#dark purple 756bb1



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
#comments_df = pd.read_sql(sql="select * from comm_subm limit 10000", con=engine)
#submissions_df = pd.read_sql(sql="select * from submissions", con=engine)

slang = pd.read_csv("internet_slang.csv")
slang_terms = [i.lower() for i in slang.term]

swear_words = open("swear_words.txt", 'r')
swear_words = swear_words.readlines()
swears = [i.split(':')[0] for i in swear_words[1:-1]]
swears2 = [i[1:-1].lower() if i[0] == '"' else i.lower() for i in swears]

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
    #df['polarity'] = df.content.apply(lambda x : TextBlob(x).polarity)
    #df['subjectivity'] = df.content.apply(lambda x : TextBlob(x).subjectivity)
    df['num_capital'] = df.content.apply(lambda x : sum([1 for i in x if i.isupper()]))
    df['num_capital_log'] = np.log10(df.num_capital)
    df['percent_capital'] = df.num_capital/df.comment_length
    df['percent_capital_log'] = df.num_capital_log - df.comment_length_log
    df['percent_capital_root'] = np.sqrt(df.percent_capital)
    df['num_slang'] = df.content.apply(lambda x : sum([1 for w in TextBlob(x).tokenize() if w.lower() in slang_terms]))
    df['num_slang_log'] = np.log10(df.num_slang)
    df['percent_slang'] = df.num_slang/df.comment_num_words
    df['percent_slang_log'] = df.num_slang_log - df.comment_num_words_log
    df['percent_slang_root'] = np.sqrt(df.percent_slang)
    df['num_punc'] = df.content.apply(lambda x : sum([1 for i in x if i in string.punctuation]))
    df['num_punc_log'] = np.log10(df.num_punc)
    df['percent_punc'] = df.num_punc/df.comment_length
    df['percent_punc_log'] = df.num_punc_log - df.comment_length_log
    df['num_swears'] = df.content.apply(lambda x : sum([1 for w in TextBlob(x).tokenize() if w.lower() in swears2]))
    df['num_swears_log'] = np.log10(df.num_swears)
    df['percent_swears'] = df.num_swears/df.comment_num_words
    df['percent_swears_log'] = df.num_swears_log - df.comment_num_words_log
    df['percent_swears_root'] = np.sqrt(df.percent_swears)
    df['avg_word_length'] = df.comment_length/df.comment_num_words
    df['avg_word_length_log'] = df.comment_length_log - df.comment_num_words_log

def scatter(x, y, c='b', cmap=None, s=10, alpha=0.2, edgecolor='', xlabel=None, ylabel=None, title=None, pic_title=None, loc=0):
    plt.clf()
    plt.scatter(x, y, c=c, cmap=cmap, s=s, alpha=alpha, edgecolor='')
    if title:
        plt.title(title)
    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)
    
    #make_legend
    for cls in classes:
        if cls == 'good' or cls == 'bad':
            plt.scatter([],[],c=colors[classes[cls]],label=cls)
    plt.legend(fontsize=6, loc=loc)
    
    if pic_title:
        plt.savefig(pic_title, dpi=300)
        
def scatter_df(df, xcol, ycol, c=None, cmap=None, s=10, alpha=0.2, edgecolor='', xlabel=None, ylabel=None, title=None, pic_title=None, loc=0):
        if c:
            c=df[c]
            cmap = lcm
        else:
            c='b'
        scatter(x=df[xcol], y=df[ycol], c=c, cmap=cmap, s=s, alpha=alpha, edgecolor=edgecolor, xlabel=xlabel, ylabel=ylabel, title=title, pic_title=pic_title, loc=loc)
        
        
        
 




