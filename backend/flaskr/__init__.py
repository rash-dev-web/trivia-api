import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import desc, not_
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    # app.debug = True
    # app.env='development'
    setup_db(app)
    

    

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)

    # @app.route('/')
    # def hello():
    #     return jsonify({'message': 'hello'})
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def get_categories():
        # categories=Category.query.order_by(desc(Category.id)).all()
        categories = Category.query.order_by(Category.id).all()
        formatted_categories = {category.id: category.type for category in categories}

        if len(formatted_categories) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': formatted_categories 
            })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods=['GET'])
    def get_questions():
        
            page = request.args.get('page', 1, type=int)
            start = (page -1) * 10
            end = start + 10
            questions = Question.query.all()
            formatted_questions = [question.format() for question in questions]
            if len(formatted_questions) == 0:
                abort(404)
            return jsonify({
                'success': True,
                'questions': formatted_questions[start:end],
                'total_questions': len(formatted_questions),
                'categories': {category.id: category.type for category in Category.query.all()},
                'current_category': 'None'
                })
        

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        
            question = Question.query.filter(Question.id == question_id).one_or_none()
            print(question)
            if question is None:
                abort(404)
            question.delete()

            return jsonify({
                "success" : True
        })
        


    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def add_questions():       

        
            body = request.get_json()
            new_question = body.get('question')
            new_answer = body.get('answer')
            new_category = body.get('category')
            new_difficulty = body.get('difficulty')
            if 'question' not in body or 'answer' not in body or 'category' not in body or 'difficulty' not in body:
                abort(400)
            question = Question(
                question=new_question,
                answer= new_answer,
                category= new_category,
                difficulty= new_difficulty
                )
            question.insert()
            formatted_questions = [question.format() for question in Question.query.all()]
            return jsonify({
                'success': True,
                'created': question.id,
                'questions': formatted_questions,
                'total_questions': len(formatted_questions)
            })
        

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_questions_by_term():
        
            body = request.get_json()
            search_term = body.get('searchTerm')
            search_results = Question.query.filter(
                Question.question.ilike("%{}%".format(search_term))).all()
            formatted_questions = [question.format() for question in search_results]
            if len(formatted_questions) == 0:
                 abort(404)
            if search_term == None:
                abort(400)
            else:
                return jsonify({
                    'success': True,
                    'questions': formatted_questions,
                    'total_questions': len(formatted_questions)

                })
        

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        
                questions = Question.query.filter(Question.category == category_id).all()
                formatted_questions = [question.format() for question in questions]
                if len(formatted_questions) == 0:
                    abort(404)
                else:
                    return jsonify({
                        'success': True,
                        'questions': formatted_questions,
                        'total_questions': len(formatted_questions),
                        'current_category': category_id
                    })
            

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def get_questions_for_quizz():
        
            body = request.get_json()
            quiz_category = body.get('quiz_category', random.randint(1, 7))
            previous_questions = body.get('previous_questions', 12)
            # quiz_category = 4
            # previous_questions = 12
            
            if 'quiz_category' not in body or 'previous_questions' not in body:
                abort(400)

            if quiz_category == 0:
                random_questions = Question.query.filter(not_(Question.id == previous_questions)).all()
            else:
                random_questions = Question.query.filter(not_(Question.id == previous_questions), Question.category == quiz_category).all() 
            
            random_question = random.choice(random_questions)
            return jsonify({
                'success': True,
                'question': random_question.format()

            })
        
        

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
        "success": False, 
        "error": 404,
        "message": "Not found"
        }), 404
    
    @app.errorhandler(422)
    def unprocessable_content(error):
        return jsonify({
        "success": False, 
        "error": 422,
        "message": "Unprocessable Content"
        }), 422
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
        "success": False, 
        "error": 400,
        "message": "Bad Request"
        }), 400
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
        "success": False, 
        "error": 500,
        "message": "Internal Server Error"
        }), 500

    return app
