from app import app, db
from models import Book
import pandas as pd

# Load book data from CSV
book_data = pd.read_csv('book_data.csv')

with app.app_context():
    db.create_all()
    
    for index, row in book_data.iterrows():
        book = Book(title=row['title'], author=row['author'], genre=row['genre'], description=row['description'])
        db.session.add(book)
    
    db.session.commit()
