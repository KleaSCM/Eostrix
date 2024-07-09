from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from app import app, db, mail
from models import User, Book, Favorite, Rating
from forms import RegistrationForm, LoginForm
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# Load book data
book_data = pd.read_csv('book_data.csv')

def recommend_books(title, book_data):
    tfidf = TfidfVectorizer(stop_words='english')
    book_data['description'] = book_data['description'].fillna('')
    tfidf_matrix = tfidf.fit_transform(book_data['description'])
    
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    
    indices = pd.Series(book_data.index, index=book_data['title']).drop_duplicates()
    
    if title not in indices:
        return []
    
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:6]
    
    book_indices = [i[0] for i in sim_scores]
    
    return book_data['title'].iloc[book_indices]

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Login unsuccessful. Please check your email and password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/recommend', methods=['POST'])
@login_required
def recommend():
    user_input = request.form['user_input']
    recommended_books = recommend_books(user_input, book_data)
    return render_template('recommendations.html', recommended_books=recommended_books)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    results = Book.query.filter(
        (Book.title.contains(query)) |
        (Book.author.contains(query)) |
        (Book.genre.contains(query))
    ).all()
    return render_template('search_results.html', results=results)

@app.route('/book/<int:book_id>')
def book_details(book_id):
    book = Book.query.get_or_404(book_id)
    ratings = Rating.query.filter_by(book_id=book_id).all()
    return render_template('book_details.html', book=book, ratings=ratings)

@app.route('/book/<int:book_id>/favorite', methods=['POST'])
@login_required
def favorite_book(book_id):
    favorite = Favorite(user_id=current_user.id, book_id=book_id)
    db.session.add(favorite)
    db.session.commit()
    flash('Book added to favorites!', 'success')
    return redirect(url_for('book_details', book_id=book_id))

@app.route('/book/<int:book_id>/rate', methods=['POST'])
@login_required
def rate_book(book_id):
    rating = request.form['rating']
    review = request.form['review']
    new_rating = Rating(user_id=current_user.id, book_id=book_id, rating=rating, review=review)
    db.session.add(new_rating)
    db.session.commit()
    flash('Thank you for your review!', 'success')
    return redirect(url_for('book_details', book_id=book_id))

@app.route('/send_email', methods=['POST'])
@login_required
def send_email():
    email = request.form['email']
    msg = Message('New Book Recommendation', sender='your_email@example.com', recipients=[email])
    msg.body = 'Check out these new book recommendations...'
    mail.send(msg)
    flash('Email sent successfully!', 'success')
    return redirect(url_for('index'))
