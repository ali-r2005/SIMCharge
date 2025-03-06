from flask import Flask
from flask_migrate import Migrate
from config import Config
from extensions import db, login

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions here to avoid circular import
db.init_app(app)
login.init_app(app)
migrate = Migrate(app, db)

# Import models after db is initialized
from models import User, ClientNumber
import routes  

if __name__ == "__main__":
    app.run(debug=True)