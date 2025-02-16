from flask import Flask, render_template
from app.extensions import db, login_manager, migrate
from app.auth.routes import auth_bp
from app.admin.routes import admin_bp
from app.performer.routes import performer_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Initialize Extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(performer_bp, url_prefix="/performer")

    # Add a root route
    @app.route('/')
    def home():
        return render_template('index.html')

    return app
