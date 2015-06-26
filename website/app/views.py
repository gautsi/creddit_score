from flask import render_template, request
from app import app
#import text_model as md
import time as tm
import pickle


@app.route('/')
def cities_output():
  #pull 'ID' from input field and store it
  #thread_url = request.args.get('thread')
  comment = request.args.get('comment')

  model_file = open('mnb_dump_2', 'r')
  model = pickle.load(model_file)  

  suggestions = []
  
  if comment is None:
    score = ''
    comment = ''

  else:

    score = model.predict_proba([comment])[0][0]
    
    score = round(100*score)
    
  return render_template("index.html", comment = comment, score = score)
  
  
