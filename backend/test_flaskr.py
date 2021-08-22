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
        self.database_path = "postgresql://postgres:12345@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        
        self.new_question = {
            'question': 'new question ',
            'answer': 'new answer',
            'difficulty': 1,
            'category': '1'
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

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
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
        
        
    
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()