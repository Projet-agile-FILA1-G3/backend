import os

from flask import Flask
from flask_cors import CORS

from shared.db import init_db

if os.getenv('ENV') != 'production':
    from dotenv import load_dotenv
    load_dotenv()

from api.controller import search, app

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
