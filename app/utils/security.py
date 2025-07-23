from flask_bcrypt import generate_password_hash, check_password_hash

def hash_password(password):
    return generate_password_hash(password).decode('utf-8')

def verify_password(password, hashed):
    return check_password_hash(hashed, password) 