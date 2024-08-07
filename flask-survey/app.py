from flask import Flask, request, render_template, redirect, make_response, flash, session
from surveys import surveys
app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"

CURRENT_KEY = 'current_key'
ANSWERS = 'answers' 

@app.route('/')
def go_home():
  """home page including list of surveys"""
  return render_template("home.html", surveys = surveys)

@app.route('/', methods=["POST"])
def go_survey():
  """page to take surveys on"""
  survey_key =  request.form["survey_key"]
  survey = surveys[survey_key]

  if request.cookies.get(f"finished_{survey_key}"):
    return render_template("finished.html")
  
  session[CURRENT_KEY] = survey_key
  return render_template("start.html", survey = survey)

@app.route('/begin', methods=["POST"])
def take_survey():
  """clear the responses"""
  session[ANSWERS] = []
  return redirect("/survey/0")

@app.route('/survey/<int:qkey>')
def go_question(qkey):
  """display next question"""

  answers = session[ANSWERS]
  key = session[CURRENT_KEY]
  survey = surveys[key]

  if answers is None:
    return redirect('/')
  if (len(answers) == len(survey.questions)):
    return redirect('/survey_done')
  if (len(answers) != qkey):
    flash(f"Incorrect question key: {qkey}.")
    return redirect(f"/survey/{len(answers)}")
  
  query = survey.questions[qkey]
  return render_template("survey.html",
                         query_key = qkey,
                         query = query)

@app.route('/answer', methods=["POST"])
def answer_query():
  """save answer and continue to next query"""
  choice = request.form['answer_key']
  text = request.form.get("text_input", "")

  answers = session[ANSWERS]
  answers.append({'choice': choice, 'text': text})

  session[ANSWERS] = answers
  key = session[CURRENT_KEY]
  survey = surveys[key]

  if (len(answers) == len(survey.questions)):
    return redirect("/survey_done")
  else:
    return redirect(f"/survey/{len(answers)}")

@app.route('/survey_done')
def go_done():
  key = session[CURRENT_KEY]
  survey = surveys[key]
  answers = session[ANSWERS]

  html = render_template("done.html",
                         survey = survey,
                         answers =answers)
  res = make_response(html)
  res.set_cookie(f"finished_{key}", 'yes', max_age = 60)
  return res