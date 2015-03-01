import argparse
import json
import os

import gnupg
from flask import Flask
from flask.ext.restful import Api, abort, reqparse, Resource
from pysswords.db import Database as PysswordsDatabase, DatabaseExistsError
from pysswords.db.credential import CredentialNotFoundError


passphrase = None
db = None


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
    parser = reqparse.RequestParser()
    parser.add_argument('login', type=str)
    parser.add_argument('password', type=str)
    parser.add_argument('comment', type=str)

    def get(self, name):
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
        global passphrase, db

        args = self.parser.parse_args()
        login = args['login']
        password = args['password']
        comment = args['comment']

        password = db.decrypt(password, passphrase)

        db.add(name, login, password, comment)
        return json.dumps({
                'name': name,
                'login': login,
                'password': password,
                'comment': comment}), 201


app = Flask(__name__)
api = Api(app)
api.add_resource(Credential, '/credentials/<string:name>')


def main():
    global db, passphrase

    parser = argparse.ArgumentParser()
    parser.add_argument('passphrase',
                        help='The passphrase used to encrypt and decrypt passwords')
    parser.add_argument('-D', '--database', default=os.path.expanduser('~/.pysswords'),
                        help='Specify the path to the pysswords database')
    parser.add_argument('-p', '--port', default=5000,
                        help='Specify which port the API should listen on')
    args = parser.parse_args()

    passphrase = args.passphrase
    db = open_db(args.database)
    app.run(debug=True, port=args.port)


if __name__ == '__main__':
    main()

