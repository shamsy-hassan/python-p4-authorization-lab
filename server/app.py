#!/usr/bin/env python3

from flask import Flask, request, session, jsonify
from flask_migrate import Migrate
from flask_cors import CORS

from models import db, User, Article

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['SECRET_KEY'] = 'mysecret'  # for session management

db.init_app(app)
migrate = Migrate(app, db)
CORS(app, supports_credentials=True)

# Helper function to check authentication
def is_authenticated():
    return 'user_id' in session

# ============================
# Routes
# ============================

@app.route('/clear')
def clear_session():
    session.clear()
    return {}, 204

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    user = User.query.filter_by(username=username).first()

    if user:
        session['user_id'] = user.id
        return user.to_dict(), 200
    else:
        return {'error': 'Unauthorized'}, 401

@app.route('/check_session')
def check_session():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return user.to_dict(), 200
    return {}, 204

@app.route('/logout', methods=['DELETE'])
def logout():
    session.clear()
    return {}, 204

# Public route
@app.route('/articles')
def get_articles():
    articles = Article.query.filter_by(is_member_only=False).all()
    return jsonify([a.to_dict() for a in articles]), 200

# Member-only index route
@app.route('/members_only_articles')
def get_member_only_articles():
    if not is_authenticated():
        return {'error': 'Please log in to access member-only content'}, 401

    articles = Article.query.filter_by(is_member_only=True).all()
    return jsonify([a.to_dict() for a in articles]), 200

# Member-only detail route
@app.route('/members_only_articles/<int:id>')
def get_member_only_article(id):
    if not is_authenticated():
        return {'error': 'Please log in to access member-only content'}, 401

    article = Article.query.get(id)
    if not article:
        return {'error': 'Article not found'}, 404
    
    return article.to_dict(), 200

# ============================

if __name__ == '__main__':
    app.run(port=5555, debug=True)