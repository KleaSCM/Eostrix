from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Book, Rating  # Import the Rating model
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        flash('Login unsuccessful. Please check your credentials.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    api_key = 'your_google_books_api_key'
    url = f'https://www.googleapis.com/books/v1/volumes?q={query}&key={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        results = []
        for item in data.get('items', []):
            volume_info = item.get('volumeInfo', {})
            results.append({
                'id': item.get('id'),
                'title': volume_info.get('title'),
                'authors': ', '.join(volume_info.get('authors', [])),
                'publishedDate': volume_info.get('publishedDate'),
                'description': volume_info.get('description'),
                'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail')
            })
        return render_template('search_results.html', results=results)
    return "An error occurred while searching for books."

@app.route('/rate/<book_id>', methods=['GET', 'POST'])
@login_required
def rate(book_id):
    if request.method == 'POST':
        rating_value = request.form.get('rating')
        rating = Rating(user_id=current_user.id, book_id=book_id, rating=rating_value)
        db.session.add(rating)
        db.session.commit()
        flash('Rating submitted successfully.')
        return redirect(url_for('home'))
    return render_template('rate.html', book_id=book_id)

if __name__ == '__main__':
    app.run(debug=True)
