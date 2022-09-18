import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
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
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    @app.route('/categories')
    def get_categories():
        categories = Category.query.order_by(Category.id).all()
        formatted_categories = [Category.format() for category in categories]
        return jsonify({
            'success': True,
            'categories': categories
        })

    @app.route('/questions?page=<int:page>', method=['GET'])
    def get_questions():

        categories = Category.query.order_by(Category.id).all()
        formatted_categories = [Category.format() for category in categories]
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'totalQuestions': len(selection.all()),
            'categories': categories,
            'currentCategory': formatted_categories

        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):

        try:
            question = Question.Query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'deleted': question.id,
                'questions': current_questions,
                'totalQuestions': len(selection.all())
            })

        except():
            abort(422)

    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)

        try:
            question = Question(question=new_question, answer=new_answer,
                                category=new_category, difficulty=new_difficulty)
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'created': question.id,
                'totalQuestions': len(selection.all())
            })

        except():
            abort(422)

    @app.route('/questions/search', methods=['POST'])
    def search_question():
        body = request.get_json()

        search_term = body.get('searchTerm', None)

        try:
            selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search_term)))
            current_search = paginate_questions(request, selection)
            categories = Category.query.order_by(Category.id).all()
            formatted_categories = [Category.format() for category in categories]

            return jsonify({
                'success': True,
                'questions': current_search,
                'totalQuestions': len(selection.all()),
                'currentCategory': formatted_categories[current_search[0]['category']-1['type']]
            })

        except():
            abort(404)

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_category(category_id):

        body = request.get_json()

        try:
            categories = Category.query.filter(category_id == Category.id).one_or_none()
            selection = Question.query.order_by(Question.id).all()
            categories = Category.query.order_by(Category.type).all()
            current_questions = paginate_questions(request, selection)
            formatted_categories = [Category.format() for category in categories]

            return jsonify({
                'success': True,
                'questions': current_questions,
                'totalQuestions': len(selection.all()),
                'categories': formatted_categories
            })

        except():
            abort(404)

    @app.route('/quizzes', methods=['POST'])
    def get_quizzes():
        quiz = request.get_json()

        try:
            previous_questions = quiz.get('previous_questions', None)
            quiz_category = quiz.get('quiz_category', None)
            category_id = quiz.get[quiz_category]['id']
            current_question = None

            if category_id != 0:
                questions = Question.query.filter(Question.category == category_id).all()

            else:
                questions = Question.query.all()
            if questions:
                current_question = random.choice(questions)

            return jsonify({
                'success': True,
                'questions': current_question

            })

        except():
            abort(422)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
        }), 422

    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'method not allowed'
        }), 405

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'bad request'
        }), 400

    return app

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """

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

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

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

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    return app
