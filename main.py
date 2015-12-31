# -*- coding: utf-8 -*-

import os
import csv
from bottle import route, run, template, redirect
from urllib2 import unquote

index_html = '''
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
    <meta name="description" content="">
    <meta name="author" content="">

    <title>{{ game_title }}</title>

    <!-- Bootstrap core CSS -->
    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" rel="stylesheet" integrity="sha256-7s5uDGW3AHqw6xtJmNNtr+OBRJUlgkNJEo78P4b0yRw= sha512-nNo+yCHEyn0smMxSswnf/OnX6/KwJuZTlNZBjauKhTK0c+zT+q5JOCx0UFhXQ6rJR9jg6Es8gPuD2uZcYDLqSw==" crossorigin="anonymous">
  </head>

  <body>

    <nav class="navbar navbar-inverse navbar-fixed-top">
      <div class="container">
        <div class="navbar-header">
          <a class="navbar-brand" href="#">{{ game_header }}</a>
        </div>
      </div>
    </nav>

    <!-- Main jumbotron for a primary marketing message or call to action -->
    <div class="jumbotron">
      <div class="container">
        {{ !game_teaser }}
      </div>
    </div>

    <div class="container">

      {{ !game_content}}

      <footer>
        <p>&copy; Georg Vogelhuber jgvogelhuber@gmail.com</p>
      </footer>
    </div> <!-- /container -->


    <!-- Bootstrap core JavaScript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
    <script>window.jQuery || document.write('<script src="../../assets/js/vendor/jquery.min.js"><\/script>')</script>
    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" rel="stylesheet" integrity="sha256-7s5uDGW3AHqw6xtJmNNtr+OBRJUlgkNJEo78P4b0yRw= sha512-nNo+yCHEyn0smMxSswnf/OnX6/KwJuZTlNZBjauKhTK0c+zT+q5JOCx0UFhXQ6rJR9jg6Es8gPuD2uZcYDLqSw==" crossorigin="anonymous">
  </body>
</html>
'''


@route('/')
def index():
    content = ""
    if len(game_played) < len(game_questions):
        content = '<div class="row">'
        for category in game_categories:
            category_questions = ""
            for score_val in game_scores:
                if (category, score_val) not in game_played:
                    category_questions += '''
                        <p align="center"><h2><a href="/question/%s/%d">%d</a></h2></p>
                    ''' % (category, score_val, score_val)
                else:
                    category_questions += "<p><h2>&nbsp;</h2></p>"

            content += '''
                <div class="col-md-4">
                    <h2>%s</h2>
                    %s
                </div>
            ''' % (category, category_questions)
        content += r'</div>'
        teaser = "<br><h3>%s bitte wählen sie eine Frage</h3>" % game_active_team
    else:
        content = "<h2>%s: %d</h2><br><h2>%s: %d</h2></br>" % (game_team_1, game_score_1, game_team_2, game_score_2)
        teaser = "<h1>Endstand<h1>"
    return template(index_html,
        game_title= game_team_1 + " vs " + game_team_2,
        game_header = "%s %d - %d %s" %
            (game_team_1, game_score_1, game_score_2, game_team_2),
        game_teaser = teaser,
        game_content = content)


@route('/question/<category>/<score>')
def question(category, score):
    current_question = None
    for question in game_questions:
        if question["category"] == unquote(category) and question["score"] == score:
            current_question = question
            break

    return template(index_html,
    game_title = game_team_1 + " vs " + game_team_2,
    game_header ="Frage für Team %s" % game_active_team,
    game_teaser = "<br><h2>Kategorie %s für %d Punkte</h2>" % (category, int(score)),
    game_content = """<div class='container'><h1>%s</h1></div>
    <div class="container"><h3><a href="/answer/%s/%s">Zur Antwort</a></h3></div>
    """ % (current_question["question"], category, score))

@route('/answer/<category>/<score>')
def answer(category, score):
    current_question = None
    for question in game_questions:
        if question["category"] == unquote(category) and question["score"] == score:
            current_question = question
            break

    return template(index_html,
    game_title = game_team_1 + " vs " + game_team_2,
    game_header ="Frage für Team %s" % game_active_team,
    game_teaser = "<br><h2>Kategorie %s für %d Punkte</h2>" % (category, int(score)),
    game_content = """<div class='container'><h1>Die richtige Antwort lautet: "%s"</h1></div>
    <div class="container"><h3><a href="/correct/%s/%s">Antwort ist richtig</a></h3>
    <h3><a href="/wrong/%s/%s">Antwort ist falsch</a></h3></div>
    """ % (current_question["answer"], category, score, category, score))

@route('/wrong/<category>/<score>')
def wrong(category, score):
    global game_active_team
    global game_score_1
    global game_score_2
    game_played.append((unquote(category), int(score)))
    if game_active_team == game_team_1:
        game_score_2 += int(score)
        game_active_team = game_team_2
    else:
        game_score_1 += int(score)
        game_active_team = game_team_1
    redirect("/")

@route('/correct/<category>/<score>')
def correct(category, score):
    global game_active_team
    global game_score_1
    global game_score_2
    game_played.append((unquote(category), int(score)))
    if game_active_team == game_team_1:
        game_score_1 += int(score)
        game_active_team = game_team_2
    else:
        game_score_2 += int(score)
        game_active_team = game_team_1
    redirect("/")

def read_game_data():
    questions = []
    categories = []
    scores = []
    with open("questions.csv","r") as f:
        reader = csv.DictReader(f)

        for entry in reader:
            questions.append(entry)
            categories.append(entry["category"])
            scores.append(int(entry["score"]))

        categories = sorted(list(set(categories)))
        scores = sorted(list(set(scores)))

    return questions, categories, scores


if __name__ == '__main__':
    game_questions, game_categories, game_scores = read_game_data()
    game_team_1 = raw_input("Name für Team 1? ")
    game_team_2 = raw_input("Name für Team 2? ")
    game_team_1 = game_team_1.strip()
    game_team_2 = game_team_2.strip()
    game_score_1 = 0
    game_score_2 = 0
    game_played = []
    game_active_team = game_team_1

    assert game_questions
    assert game_categories
    assert game_scores
    assert game_team_1
    assert game_team_2

    port = int(os.environ.get('PORT', 8080))
    run(host='0.0.0.0', port=port, debug=True)
