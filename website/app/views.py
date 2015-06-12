from flask import render_template, request
from app import app
import model as md
import time as tm

@app.route('/')
def cities_output():
  #pull 'ID' from input field and store it
  thread_url = request.args.get('thread')
  comment = request.args.get('comment')
  
  if comment is None:
    score = ''
    comment = ''
    thread_url = ''
  else:
    subm = md.red.get_submission(url=thread_url)
    score = md.model.predict([subm.score, subm.num_comments, tm.time() - subm.created_utc, len(comment)])
    score = int(round(score))

  return render_template("index.html", thread_url = thread_url, comment = comment, score = score)
  
