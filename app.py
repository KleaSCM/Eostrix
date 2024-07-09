from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['GOOGLE_BOOKS_API_KEY'] = 'AIzaSyAp7SmJS5G5eAz837ar2K_w91pb6JLRMPA'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    name = db.Column(db.String(150))

class Book(db.Model):
    id = db.Column(db.String(20), primary_key=True)
    title = db.Column(db.String(150))
    authors = db.Column(db.String(150))
    description = db.Column(db.Text)
    thumbnail = db.Column(db.String(200))
    published_date = db.Column(db.String(20))

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.String(20), db.ForeignKey('book.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password, method='sha256')
        
        new_user = User(email=email, name=name, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
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
        else:
            flash('Login failed. Check your email and password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/search')
def search():
    query = request.args.get('q')
    results = []
    if query:
        response = requests.get(f'https://www.googleapis.com/books/v1/volumes?q={query}&key={app.config["GOOGLE_BOOKS_API_KEY"]}')
        if response.status_code == 200:
            books = response.json().get('items', [])
            for book in books:
                volume_info = book.get('volumeInfo', {})
                image_links = volume_info.get('imageLinks', {})
                results.append({
                    'id': book.get('id'),
                    'title': volume_info.get('title'),
                    'authors': ', '.join(volume_info.get('authors', [])),
                    'description': volume_info.get('description'),
                    'publishedDate': volume_info.get('publishedDate'),
                    'thumbnail': image_links.get('thumbnail')
                })
    return render_template('search_results.html', results=results)

@app.route('/rate/<book_id>', methods=['GET', 'POST'])
@login_required
def rate(book_id):
    if request.method == 'POST':
        rating_value = request.form.get('rating')
        rating = Rating(user_id=current_user.id, book_id=book_id, rating=rating_value)
        db.session.add(rating)
        db.session.commit()
        flash('Rating submitted!', 'success')
        return redirect(url_for('home'))
    return render_template('rate.html', book_id=book_id)

if __name__ == '__main__':
    app.run(debug=True)
