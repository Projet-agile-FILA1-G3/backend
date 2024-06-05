import os

from flask import Flask
from flask_cors import CORS

if os.getenv('ENV') != 'production':
    from dotenv import load_dotenv
    load_dotenv()

from api.controller import search, app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', os.getenv('PORT', 5000))))
