import json
import os

from flask import Flask
from flask.ext.restful import Api, abort, reqparse, Resource
from pysswords.db import Database as PysswordsDatabase, DatabaseExistsError
from pysswords.db.credential import CredentialNotFoundError


parser = reqparse.RequestParser()
parser.add_argument('database', type=str)
parser.add_argument('name', type=str)
parser.add_argument('login', type=str)
parser.add_argument('password', type=str)
parser.add_argument('comment', type=str)


def open_db(path):
    '''Open and return a handle to a Pysswords database.
    Returns None if the database corresponding to a path can't be found.
    '''
    try:
        return PysswordsDatabase(path)
    except DatabaseExistsError:
        return None


def open_credentials(db, credential_name):
    '''Return all the given credentials for a domain.
    None is returned if no credentials are found.

    Example:
        db = open_db('/home/andrew/.pysswords')
        credentials = open_credentials(db, 'google.com')
    '''
    try:
        return db.get(credential_name)
    except CredentialNotFoundError:
        return None


class Credential(Resource):
    def get(self, name):
	args = parser.parse_args()
        db_path = args['database']
        if db_path is None:
            db_path = os.expanduser('~/.pysswords')

        db = open_db(db_path)
        if db is None:
            msg = "Database {} doesn't exist".format(db_path)
            return msg, 404
        
        credentials = open_credentials(db, name)
        if credentials is None:
            msg = "No credentials found for name: {}".format(name)
	    return msg, 404

        response = []
        for credential in credentials:
            response.append({
                'name': name,
                'login': credential.login,
                'password': credential.password,
                'comment': credential.comment})
	return json.dumps(response), 200
        
    def put(self, name):
        args = parser.parse_args()
        db_path = args['database']
        login = args['login']
        password = args['password']
        comment = args['comment']

        db = open_db(db_path)
        if db is None:
            msg = "Database {} doesn't exist".format(db_path)
            return msg, 404

        db.add(name, login, password, comment)
        return json.dumps({'name': name, 'login': login,
            'password': password, 'comment': comment}), 201


app = Flask(__name__)
api = Api(app)
api.add_resource(Credential, '/credentials/<string:name>')


if __name__ == '__main__':
    app.run(debug=True)

