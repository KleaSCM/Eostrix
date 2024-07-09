from app import db, User, Book, Rating

db.drop_all()
db.create_all()

# Optionally, create some initial data
user = User(email='admin@example.com', name='Admin User', password='admin')
db.session.add(user)
db.session.commit()
