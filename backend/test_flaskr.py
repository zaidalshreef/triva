import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}@{}/{}".format(os.getenv('server'),'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        
        self.new_question = {
            'question': 'new question ',
            'answer': 'new answer',
            'difficulty': 1,
            'category': 1
        }


        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_paginate(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
            
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
        self.assertEqual(data['current_category'],None)
        
    def test_404_not_valid_page(self):
        res = self.client().get('/questions?page=10000')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],"The server can not find the requested resource")

    def test_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        
    def test_404_sent_not_existing_category(self):
        res = self.client().get('/categories/100000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'The server can not find the requested resource')
        
    def test_questions_deleted(self):
        question = Question(question=self.new_question['question'],
                                answer=self.new_question['answer'],
                                category=self.new_question['category'],
                                difficulty=self.new_question['difficulty'])
        question.insert()
        id = question.id
        questions = Question.query.all()
        res = self.client().delete('/questions/{}'.format(id))
        data = json.loads(res.data)
        
        questions_after_delete = Question.query.all()
        deleted_question = Question.query.get(id)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'],id)
        self.assertEqual(len(questions),len(questions_after_delete)+1)
        self.assertEqual(deleted_question,None)
        
    def test_422_if_question_not_exist(self):
        res = self.client().delete('/questions/100000')
        data = json.loads(res.data)
      
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'The request was well-formed but was unable to be followed due to semantic errors.')
        
    def test_add_new_question(self):
   
        questions = Question.query.all()

        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        questions_after_add = Question.query.all()
        new_question_id = data['created']

        question = Question.query.filter_by(id=new_question_id)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(questions_after_add), len(questions)+1)
        self.assertIsNotNone(question)
   
    def test_422_add_new_question(self):
        new_question = {
            'question': 'new question ',
            'difficulty': 1,
            'category': 1
        }

        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'The request was well-formed but was unable to be followed due to semantic errors.')
        
        
    def test_search_question(self):
        
        search_term = {
            "searchTerm": ""
        }
   
        res = self.client().post('/questions/search', json=search_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["totalQuestions"])
   
    def test_422_search_term_not_found(self):
        
        search_term = {  }
        res = self.client().post('/questions/search', json=search_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'The request was well-formed but was unable to be followed due to semantic errors.')


    def test_404_search_questions_not_found(self):
        
        search_term = {"searchTerm": "aaaaaaaaaaaaa"}
   
        res = self.client().post('/questions/search', json=search_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'The server can not find the requested resource')

    def test_search_question_by_category(self):
        
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["current_category"])
        
        
    def test_404_category_not_found(self):
        
        res = self.client().get('/categories/xx/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'The server can not find the requested resource')

    def test_play_quizzes(self):
        quiz = {
            'previous_questions': [],
            'quiz_category': {'type': 'Science', 'id': 1}
        }
        res = self.client().post('/quizzes', json=quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data["question"])

        
        
    def test_422_play_quizzes(self):
       
        res = self.client().post('/quizzes', json={})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'The request was well-formed but was unable to be followed due to semantic errors.')
    
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()