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
  CORS(app)


  @app.after_request
  def after_request(response):
    response.headers.add("Access-Control-Allow-Headers", 
                         "Content-Type, Authorization")
    response.headers.add("Access-Control-Allow-Methods",
                         "GET, PATCH, POST, PUT, DELETE, OPTIONS")
    return response

  
  @app.route("/categories")
  def get_categories():
    
    categories = Category.query.all()
    
    categories_dictionary = {}
    for category in categories:
      categories_dictionary[category.id]=category.type
      
    if (len(categories_dictionary)==0):
      abort(404)
      
    return jsonify({
                    "success": True,
                    "categories": categories_dictionary,
                    })


  @app.route("/questions")
  def get_questions():
    questions = Question.query.order_by(Question.id).all()
    total_questions = len(questions)
    current_questions = pagination_question(request,questions)
    
    categories = Category.query.all()
    categories_dictionary = {}
    for category in categories:
      categories_dictionary[category.id] =category.type
      
    if (len(current_questions)==0):
      abort(404)
               
    return jsonify({
      "success": True,
      "categories": categories_dictionary,
      "total_questions": total_questions,
      "questions": current_questions,
      "current_category" : None
      
    })


  @app.route("/questions/<int:id>",methods=["DELETE"])
  def get_questionbyid(id):
   
    question = Question.query.get(id)
    if (question is None):
      abort(422)
    try:
      question.delete()
      return jsonify({
      "success": True,
      "deleted" : id
    })
    except:
      abort(422)

  @app.route("/questions", methods=["POST"])
  def create_question():
    
    data = request.get_json()

    if not ('question' in data and 'answer' in data and 'difficulty' in data and 'category' in data):
            abort(422)

    try:
      question = Question(
        question=data.get('question'),
        answer=data.get('answer'),
        category=data.get("category"),
        difficulty=data.get('difficulty'))
      question.insert()
      questions = Question.query.order_by(Question.id).all()
      total_questions = len(questions)
      current_questions = pagination_question(request,questions)
      return jsonify({
        "success": True,
        "created": question.id,
        "questions":current_questions,
        "total_questions": total_questions,
      })
    
    except:
      abort(422)
 
 
  @app.route("/questions/search", methods=["POST"])
  def search_questions():
    data = request.get_json()
    if "searchTerm" not in data:
      abort(422)
    search_term = data.get('searchTerm')
    questions = Question.query.filter(
      Question.question.ilike('%'+search_term+'%')).all()
    current_questions = pagination_question(request,questions)
    
    if len(current_questions) == 0 :
      abort(404)
    
    return jsonify({
      'success': True,
      'questions' : current_questions,
      'totalQuestions' : len(Question.query.all()),
      'currentCategory' : None
    })

 
  
  @app.route('/categories/<int:id>/questions')
  def questionsbycategory(id):
    
    category_type = Category.query.get(id)
    if category_type is None:
      abort(404)
    
    question = Question.query.filter_by(category=category_type.id).all()
    
    current_questions = pagination_question(request, question)

        # return the results
    return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(Question.query.all()),
            'current_category': category_type.type
        })


  @app.route("/quizzes", methods=["POST"])
  def quizzes():
    
    data = request.get_json()
    
    if not('previous_questions' in data and 'quiz_category' in data):
      abort(422)
    
    previous_questions = data.get('previous_questions')
    current_category = data.get('quiz_category')
    
    if current_category['id'] == 0:
      questions = Question.query.filter(
        Question.id.notin_(previous_questions)).all()
    else:
      questions = Question.query.filter_by(
        category = current_category["id"]).filter(
          Question.id.notin_(previous_questions)).all()
    
    if (len(questions)>0):
      question = questions[random.randrange(len(questions))] 
    else:
      return jsonify({
        'success': True,
      })
    
    return jsonify({
      'success': True,
      'question':question.format()
    })
 


  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      'error': 404,
      "message" : "The server can not find the requested resource"
      }
    ),404
  
  
  @app.errorhandler(422)
  def unprocessable_entity(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "The request was well-formed but was unable to be followed due to semantic errors."
    }),422
    
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "The server could not understand the request due to invalid syntax."
    }),400
    
  return app

    