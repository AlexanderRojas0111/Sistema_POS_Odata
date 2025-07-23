from app.models import User
from app import db
from app.utils.security import hash_password

def get_all_users():
    return User.query.all()

def create_user(data):
    user = User(
        email=data.get('email'),
        password=hash_password(data.get('password')),
        name=data.get('name')
    )
    db.session.add(user)
    db.session.commit()
    return user

def get_user_by_email(email):
    return User.query.filter_by(email=email).first() 