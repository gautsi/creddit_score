from flask import render_template, request
from app import app
import model as md
import time as tm

@app.route('/')
def cities_output():
  #pull 'ID' from input field and store it
  thread_url = request.args.get('thread')
  comment = request.args.get('comment')
  
  suggestions = []
  
  if comment is None:
    score = ''
    comment = ''
    thread_url = ''
  else:
    subm = md.red.get_submission(url=thread_url)
    
    subm_score = subm.score
    subm_num_comments = subm.num_comments
    thread_age = tm.time() - subm.created_utc
    comment_length = len(comment)
    
    score = md.model.predict([subm_score, subm_num_comments, thread_age, comment_length])
    
    score = int(round(score))
    
    if thread_age > 120000:
        suggestions.append("Post to a more recent thread")
        
    if comment_length > 2000:
        suggestions.append("Try a shorter comment")
        
    if subm_num_comments < 20:
        suggestions.append("Post to a more active thread (look at number of comments)")
    
    if subm_score < 100:
        suggestions.append("Post to a more popular thread (look at the score of the thread)")

  return render_template("index.html", thread_url = thread_url, comment = comment, score = score, suggestions=suggestions)
  
