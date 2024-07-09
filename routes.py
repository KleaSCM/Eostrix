import requests
from flask import render_template, request, redirect, url_for, flash
from app import app, db
from models import Book, User
from flask_login import login_user, logout_user, login_required, current_user

def fetch_books_from_google(query):
    api_key = 'AIzaSyAp7SmJS5G5eAz837ar2K_w91pb6JLRMPA'
    url = f'https://www.googleapis.com/books/v1/volumes?q={query}&key={api_key}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get('items', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Google Books API: {e}")
        return []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query:
        flash('Please enter a search term.')
        return redirect(url_for('home'))

    results = fetch_books_from_google(query)
    return render_template('search_results.html', results=results)

@app.route('/recommend', methods=['POST'])
@login_required
def recommend():
    query = request.form.get('q')
    results = fetch_books_from_google(query)
    return render_template('recommendations.html', results=results)
