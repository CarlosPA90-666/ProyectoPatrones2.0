import mysql.connector
import click
from flask import current_app, g  
from flask.cli import with_appcontext
from .schema import instructions

def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host=current_app.config['DATABASE_HOST'],
            user=current_app.config['DATABASE_USER'],
            password=current_app.config['DATABASE_PASSWORD'],
            database=current_app.config['DATABASE']
        )
        g.c = g.db.cursor(dictionary=True)
    return g.db, g.c

def close_db(e=None):
    db = g.pop('db',None)

    if db is not None:
        db.close()

def init_db():
    db,c = get_db()
    
    for i in instructions:
        c.execute(i)
    db.commit()

def recibir_tablas() :
    db,c = get_db()
    query = 'select m.id, m.created_by, m.Contentmsg, u.family, m.created_at,'\
            'u.username from Mensaje m join Usuario u on m.created_by = u.id where u.family = "p"'
    c.execute(query)
    user = c.fetchone()
    print(user)
    c.close()

@click.command('prove-db')
@with_appcontext
def prove_db_command():
    recibir_tablas()
    click.echo('Base de datos probada')

@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Base de datos inicializada')

def init__app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(prove_db_command)