import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_cors import CORS
import random
from requests.exceptions import HTTPError


from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type, Authorization"
        )
        response.headers.add(
            "Access-Control-Allow-Headers", "GET, POST, PATCH, DELETE, OPTIONS"
        )
        return response

    # an endpoint to handle GET requests for all available categories
    @app.route("/categories", methods=["GET"])
    def get_categories():
        try:
            categories = Category.query.order_by(Category.id).all()
            formatted_categories = {
                category.id: category.type for category in categories
            }

            if len(formatted_categories) == 0:
                abort(404)

            return jsonify({"success": True, "categories": formatted_categories})

        except KeyError:
            abort(422)
        except Exception as e:
            print(e)
            abort(500)

    # an endpoint to handle GET requests for all available questions with pagination
    @app.route("/questions", methods=["GET"])
    def get_questions():
        try:
            page = request.args.get("page", 1, type=int)
            questions = Question.query.paginate(page=page, per_page=10)
            formatted_questions = [question.format() for question in questions.items]
            if len(formatted_questions) == 0:
                abort(404)
            return jsonify(
                {
                    "success": True,
                    "questions": formatted_questions,
                    "total_questions": questions.total,
                    "categories": {
                        category.id: category.type for category in Category.query.all()
                    },
                    "current_category": "None",
                }
            )
        except KeyError:
            abort(422)
        except Exception as e:
            print(e)
            abort(500)

    # an endpoint to handle DELETE requests for deleting a question
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        question = Question.query.filter(Question.id == question_id).one_or_none()
        # print(question)
        if question is None:
            abort(404)
        try:
            question.delete()

            return jsonify(
                {
                    "success": True,
                    "id": question_id})
        except Exception as e:
            print(e)
            abort(500)

    # an endpoint to handle POST requests for adding a new question
    @app.route("/questions", methods=["POST"])
    def add_questions():
        body = request.get_json()
        if (
            "question" not in body
            or "answer" not in body
            or "category" not in body
            or "difficulty" not in body
        ):
            abort(400)
        try:
            new_question = body.get("question")
            new_answer = body.get("answer")
            new_category = body.get("category")
            new_difficulty = body.get("difficulty")

            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty,
            )
            if any(value == '' for value in question.__dict__.values()):
                print("At least one value is an empty string.")
                abort(400)
            else:
                print("No empty strings found.")
            question.insert()
            formatted_questions = [
                question.format() for question in Question.query.all()
            ]
            return jsonify(
                {
                    "success": True,
                    "created": question.id,
                    "questions": formatted_questions,
                    "total_questions": len(formatted_questions),
                }
            )
        except KeyError:
            abort(422)
        except Exception as e:
            print(e)
            abort(500)

    @app.route("/questions/search", methods=["POST"])
    def search_questions_by_term():
        body = request.get_json()
        search_term = body.get("searchTerm")
        search_results = Question.query.filter(
            Question.question.ilike("%{}%".format(search_term))
        ).all()
        formatted_questions = [question.format() for question in search_results]
        if len(formatted_questions) == 0:
            abort(404)
        if search_term == None:
            abort(400)

        try:
            return jsonify(
                {
                    "success": True,
                    "questions": formatted_questions,
                    "total_questions": len(formatted_questions),
                }
            )
        except Exception as e:
            print(e)
            abort(500)

    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def get_questions_by_category(category_id):
        questions = Question.query.filter(Question.category == category_id).all()
        formatted_questions = [question.format() for question in questions]
        if len(formatted_questions) == 0:
            abort(404)
        try:
            return jsonify(
                {
                    "success": True,
                    "questions": formatted_questions,
                    "total_questions": len(formatted_questions),
                    "current_category": category_id,
                }
            )
        except Exception as e:
            print(e)
            abort(500)

    @app.route("/quizzes", methods=["POST"])
    def get_questions_for_quizz():
        body = request.get_json()
        quiz_category = body.get("quiz_category")
        previous_questions = body.get("previous_questions", [])

        if "quiz_category" not in body or "previous_questions" not in body:
            abort(400)

        if quiz_category == 0:
            random_questions = Question.query.filter(
                Question.id.not_in(previous_questions)
            ).all()
        else:
            random_questions = Question.query.filter(
                Question.id.not_in(previous_questions),
                Question.category == quiz_category,
            ).all()
        try:
            random_question = random.choice(random_questions)
            return jsonify({"success": True, "question": random_question.format()})
        except Exception as e:
            print(e)
            abort(500)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "Not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable_content(error):
        return (
            jsonify(
                {"success": False, "error": 422, "message": "Unprocessable Content"}
            ),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({"success": False, "error": 400, "message": "Bad Request"}),
            400,
        )

    @app.errorhandler(500)
    def internal_server_error(error):
        return (
            jsonify(
                {"success": False, "error": 500, "message": "Internal Server Error"}
            ),
            500,
        )

    return app
