import os
from typing import Iterable
from flask import Flask, app, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def pagination_question(request,selection):
  page = request.args.get('page',1,type=int)
  start = (page - 1)* QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE 
  
  questions = [question.format() for question in selection]
  current_questions = questions[start:end]
  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  # set up the CORS
  CORS(app)

# set access control allow
  @app.after_request
  def after_request(response):
    response.headers.add("Access-Control-Allow-Headers", 
                         "Content-Type, Authorization")
    response.headers.add("Access-Control-Allow-Methods",
                         "GET, PATCH, POST, PUT, DELETE, OPTIONS")
    return response

  # get all categories in the database 
  @app.route("/categories")
  def get_categories():
    # get all categories and add it to dictionary
    categories = Category.query.all()
    categories_dictionary = {}
    for category in categories:
      categories_dictionary[category.id]=category.type
      
      # abort if no categories found
    if (len(categories_dictionary)==0):
      abort(404)
      
    return jsonify({
                    "success": True,
                    "categories": categories_dictionary,
                    })


# get all questions in database 
  @app.route("/questions")
  def get_questions():
    # get all questions order_by id 
    questions = Question.query.order_by(Question.id).all()
    # get the total number of questions
    total_questions = len(questions)
    # paginate the questions
    current_questions = pagination_question(request,questions)
    # get all categories and add it to dictionary
    categories = Category.query.all()
    categories_dictionary = {}
    for category in categories:
      categories_dictionary[category.id] =category.type
      # abort if there is no questions
    if (len(current_questions)==0):
      abort(404)
               
    return jsonify({
      "success": True,
      "categories": categories_dictionary,
      "total_questions": total_questions,
      "questions": current_questions,
      "current_category" : None
      
    })

# delete question from database by id 
  @app.route("/questions/<int:id>",methods=["DELETE"])
  def get_questionbyid(id):
   # get question by id
    question = Question.query.get(id)
    #if there is no question by the givin id abort 
    if (question is None):
      abort(422)
    try:
      # delete question from database
      question.delete()
      return jsonify({
      "success": True,
      "deleted" : id
    })
    except:
      # abort if there is error deleting the question from database
      abort(422)
# create new question and add it to database
  @app.route("/questions", methods=["POST"])
  def create_question():
    # loads the request body 
    data = request.get_json()
# abort if the request body is invalid 
    if not ('question' in data and 'answer' in data and 'difficulty' in data and 'category' in data):
            abort(422)

    try:
      question = Question(
        question=data.get('question'),
        answer=data.get('answer'),
        category=data.get("category"),
        difficulty=data.get('difficulty'))
      # add the new question to the database
      question.insert()
      #get the questions ordered by id
      questions = Question.query.order_by(Question.id).all()
      # total number of questions in the database after insert the new question
      total_questions = len(questions)
      # paginate the questions 
      current_questions = pagination_question(request,questions)
      return jsonify({
        "success": True,
        "created": question.id,
        "questions":current_questions,
        "total_questions": total_questions,
      })
    
    except:
      abort(422)
 
 # search for questions 
  @app.route("/questions/search", methods=["POST"])
  def search_questions():
    # load the request body
    data = request.get_json()
    # abort if there is no searchTerm in the request body
    if "searchTerm" not in data:
      abort(422)
      
    # get the searchTerm
    search_term = data.get('searchTerm')
    # get the questions that have name like the searchTerm 
    questions = Question.query.filter(
      Question.question.ilike('%'+search_term+'%')).all()
    #paginate the questions
    current_questions = pagination_question(request,questions)
    # abort if there is questions 
    if len(current_questions) == 0 :
      abort(404)
    
    return jsonify({
      'success': True,
      'questions' : current_questions,
      'totalQuestions' : len(Question.query.all()),
      'currentCategory' : None
    })

 
  # get all the questions by category id 
  @app.route('/categories/<int:id>/questions')
  def questionsbycategory(id):
    # get category by id
    category_type = Category.query.get(id)
    # abort if there is no category by that id 
    if category_type is None:
      abort(404)
    # get the questions by a category id
    question = Question.query.filter_by(category=category_type.id).all()
    
    # paginate the questions by givin category id
    current_questions = pagination_question(request, question)

        # return the results
    return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(Question.query.all()),
            'current_category': category_type.type
        })

# play quizzes 
  @app.route("/quizzes", methods=["POST"])
  def quizzes():
    # loads the request body
    data = request.get_json()
    # abort if there is no previous questions or quiz category in the request body
    if not('previous_questions' in data and 'quiz_category' in data):
      abort(422)
    # get previous questions in the quizzes 
    previous_questions = data.get('previous_questions')
   # get the quiz category
    current_category = data.get('quiz_category')
    # get all questions if ALL is selected
    if current_category['id'] == 0:
      questions = Question.query.filter(
        Question.id.notin_(previous_questions)).all()
    else:
      # get the questions for given category
      questions = Question.query.filter_by(
        category = current_category["id"]).filter(
          Question.id.notin_(previous_questions)).all()
    # pick a random question if number of questions is more than 0 
    if (len(questions)>0):
      question = questions[random.randrange(len(questions))] 
    else:
      # if there is no remaining questions, return without question 
      return jsonify({
        'success': True,
      })
    # return the question 
    return jsonify({
      'success': True,
      'question':question.format()
    })
 

# handle 404 error in the application
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      'error': 404,
      "message" : "The server can not find the requested resource"
      }
    ),404
  
  #handle 422 error in the application 
  @app.errorhandler(422)
  def unprocessable_entity(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "The request was well-formed but was unable to be followed due to semantic errors."
    }),422
 # handle 400 error in the application 
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "The server could not understand the request due to invalid syntax."
    }),400
    
  return app

    