from app import app, db
from models import Book
import pandas as pd
from sqlalchemy import inspect

# Load book data from CSV
book_data = pd.read_csv('book_data.csv')

with app.app_context():
    # Drop all tables (optional, for cleanup before creating)
    print("Dropping all tables...")
    db.drop_all()
    print("Creating all tables...")
    # Create all tables
    db.create_all()
    
    # Verify that the tables were created
    inspector = inspect(db.engine)
    table_names = inspector.get_table_names()
    print(f"Tables created: {table_names}")
    
    # Check if Book table is created
    if 'book' not in table_names:
        print("Error: Book table not created!")
    else:
        print("Book table exists. Inserting data...")
        # Add book data to the database
        for index, row in book_data.iterrows():
            print(f"Inserting book: {row['title']}")
            book = Book(title=row['title'], author=row['author'], genre=row['genre'], description=row['description'])
            db.session.add(book)
        
        db.session.commit()
        print("Database initialization complete.")
# finaly 