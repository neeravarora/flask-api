from flask import request, jsonify
from itsdangerous import TimestampSigner
from functools import wraps
from src.main import app
from src.main import db
from src.models.client import Client
from src.models.user import User

secret = 'tomasz_has_a_secret'

def validate_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        headers = request.headers
        if 'token' not in headers:
            return '', 403

        token = headers['token'].encode('utf8')

        signer = TimestampSigner(secret)
        try:
            signer.unsign(token, max_age = 5 * 60);
            return f(*args, **kwargs)
        except:
            return '', 403
    return wrapper

@app.route("/v1/auth/login", methods = ['POST'])
def login():
    body = request.get_json()
    if body['login'] is None:
        return '', 403

    user = User.query.filter_by(login = body['login']).first()
    if user is None:
        return '', 403

    if user.password != body['password']:
        return '', 403

    signer = TimestampSigner(secret)
    token = signer.sign(body['login']);

    return jsonify(user = user.jsonify(), token = token )

@app.route("/v1/auth/logout", methods = ['POST'])
def logout():
    body = request.get_json()

    if body['token'] is None:
        return 'token field is required', 400

    token = body['token'].encode('utf8')

    signer = TimestampSigner(secret)
    try:
        signer.unsign(token, max_age = 5 * 60)
        invalidated_token = InvalidatedToken(body['token'])
        db.session.add(invalidated_token)
        db.session.commit()
        return '', 200
    except:
        return 'Provided token is invalid or already expired', 400
