import os
from flask import Flask, render_template
from flask_socketio import SocketIO, send

def create_app():
    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY='mikey',
        DATABASE_HOST=os.environ.get('FLASK_DATABASE_HOST'),
        DATABASE_PASSWORD=os.environ.get('FLASK_DATABASE_PASSWORD'),
        DATABASE_USER=os.environ.get('FLASK_DATABASE_USER'),
        DATABASE=os.environ.get('FLASK_DATABASE'),
    )

    socketio = SocketIO(app)

    from . import db
    db.init__app(app)

    from . import auth
    from . import aplicacion

    app.register_blueprint(auth.bp)
    app.register_blueprint(aplicacion.bp)

    @app.route('/hola')
    def hola():
        return 'Hola mundo'

    @app.route('/pruebas')
    def pruebas() :
        return render_template('pruebas.html')
    
    @socketio.on('message')
    def handleMessage(msg) :
        print('Message: '+msg)
        send(msg,broadcast=True)

    return app
