from flask import (Blueprint, flash, g, render_template,
                   request, url_for, redirect)
from werkzeug.exceptions import abort
from patrones.auth import login_require
from patrones.db import get_db
from flask_socketio import send

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from flask_socketio import send

bp = Blueprint('patrones',__name__)


@bp.route('/')
@login_require
def index():
    db, c = get_db()
    c.execute('select r.id, r.description, u.username, r.completed, r.created_at from Recordatorio r JOIN Usuario u on '
              'r.created_by = u.id where r.created_by=%s order by created_at desc', (g.user['id'],))
    recordatorios = c.fetchall()

    c.execute('select m.id, m.description, u.username, m.medicine, m.posology, m.amount from Medicamento m JOIN Usuario u on '
              'm.created_by = u.id where m.created_by=%s', (g.user['id'],))
    medicamentos = c.fetchall()

    c.execute('select c.id, c.specialization, u.username, c.date, c.doctor, c.companion from Cita c JOIN Usuario u on '
              'c.created_by = u.id where c.created_by=%s', (g.user['id'],))
    citas = c.fetchall()

    c.execute(
        'select o.id, o.name, o.bank, o.value, o.Nextpaydate from ObligacionesFinancieras o join Usuario u on o.created_by = u.id where u.id = %s', (g.user['id'],))
    obligaciones = c.fetchall()

    # c.execute('select r.id, r.description, u.username, r.completed, r.created_at from Recordatorio r JOIN Usuario u on '
    #        'r.created_by = u.id where r.created_by=%s order by created_at desc',(g.user['id'],))
    #recordatorios = c.fetchall()
    return render_template('aplicacion/recordatorios.html', recordatorios=recordatorios, medicamentos=medicamentos, citas=citas, obligaciones=obligaciones)

########################################################### RECORDATORIO ###########################################################


@bp.route('/create', methods=['GET', 'POST'])
@login_require
def create():
    if request.method == "POST":
        description = request.form['description']
        error = None

        if not description:
            error = 'Descripcion es requerida'
        if error is not None:
            flash(error)
        else:
            db, c = get_db()
            c.execute('insert into Recordatorio (created_by,description,completed)'
                      ' values (%s,%s,%s)', (g.user['id'], description, False))
        db.commit()
        return redirect(url_for('patrones.index'))

    return render_template('aplicacion/create.html')


def get_recordatorio(id):
    db, c = get_db()
    c.execute('select r.id, r.description, r.completed, r.created_by, r.created_at,'
              ' u.username from Recordatorio r join Usuario u on r.created_by = u.id where r.id = %s', (id,))
    recordatorio = c.fetchone()
    if recordatorio is None:
        abort(404, 'El todo de id {0} no existe'.format(id))
    return recordatorio


@bp.route('/<int:id>/update', methods=['GET', 'POST'])
@login_require
def update(id):
    recordatorio = get_recordatorio(id)
    if request.method == 'POST':
        description = request.form['description']
        error = None

        if error is not None:
            flash(error)
        else:
            db, c = get_db()
            c.execute('update Recordatorio set description = %s where id = %s and created_by = %s',
                      (description, id, g.user['id']))
            db.commit()
            return redirect(url_for('patrones.index'))
    return render_template('aplicacion/update.html', recordatorio=recordatorio)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_require
def delete(id):
    db, c = get_db()
    c.execute(
        'delete from recordatorio where id = %s and created_by = %s', (id, g.user['id']))
    db.commit()
    return redirect(url_for('patrones.index'))


@bp.route('/<int:id>/complete', methods=['GET', 'POST'])
@login_require
def complete(id):
    recordatorio = get_recordatorio(id)
    if request.method == 'POST':
        completed = True if request.form.get('completed') == 'on' else False
        error = None

        if error is not None:
            flash(error)
        else:
            db, c = get_db()
            c.execute('update recordatorio set completed = %s where id = %s and created_by = %s',
                      (completed, id, g.user['id']))
            db.commit()
            return redirect(url_for('patrones.index'))
    return render_template('aplicacion/complete.html', recordatorio=recordatorio)

########################################################### MEDICAMENTO ###########################################################


@bp.route('/createM', methods=['GET', 'POST'])
@login_require
def createM():
    if request.method == "POST":
        nombre = request.form['nombre_medicamento']
        description = request.form['descripcion_medicamento']
        dosis = request.form['dosis_medicamento']
        posologia = request.form['posologia_medicamento']
        precio = request.form['precio_medicamento']
        cantidad = request.form['cantidad_medicamento']

        error = None

        if not nombre:
            error = 'Nombre del Medicamento requerido'
        if error is not None:
            flash(error)
        else:
            db, c = get_db()
            c.execute('insert into Medicamento (created_by,medicine,description,dose,posology,price,amount)'
                      ' values (%s,%s,%s,%s,%s,%s,%s)', (g.user['id'], nombre, description, dosis, posologia, precio, cantidad))
        db.commit()
        return redirect(url_for('patrones.index'))

    return render_template('aplicacion/createM.html')

##########################################################################################################################################


@bp.route('/<int:id>/updateM', methods=['GET', 'POST'])
@login_require
def updateM(id):
    medicamento = get_medicamento(id)
    if request.method == 'POST':
        dosis = request.form['dosis_medicamento']
        posologia = request.form['posologia_medicamento']
        precio = request.form['precio_medicamento']
        cantidad = request.form['cantidad_medicamento']

        error = None

        if error is not None:
            flash(error)
        else:
            db, c = get_db()
            c.execute('update Medicamento set dose = %s, posology = %s, price = %s, amount = %s'
                      ' where id = %s and created_by = %s', (dosis, posologia, precio, cantidad, id, g.user['id']))
            db.commit()
            return redirect(url_for('patrones.index'))
    return render_template('aplicacion/updateM.html', medicamento=medicamento)


def get_medicamento(id):
    db, c = get_db()
    c.execute('select m.id, m.posology, m.dose, m.created_by, m.price, m.amount,'
              ' u.username from Medicamento m join Usuario u on m.created_by = u.id where m.id = %s', (id,))
    medicamento = c.fetchone()
    if medicamento is None:
        abort(404, 'El medicamento de id {0} no existe'.format(id))
    return medicamento

##########################################################################################################################################


@bp.route('/<int:id>/deleteM', methods=['POST'])
@login_require
def deleteM(id):
    db, c = get_db()
    c.execute(
        'delete from Medicamento where id = %s and created_by = %s', (id, g.user['id']))
    db.commit()
    return redirect(url_for('patrones.index'))

########################################################### CITAS MEDICAS ###########################################################


@bp.route('/createC', methods=['GET', 'POST'])
@login_require
def createC():
    if request.method == "POST":
        date = request.form['fecha_cita']
        doctor = request.form['doctor_cita']
        specialization = request.form['especialidad_cita']
        companion = request.form['acompanante_cita']

        error = None

        if not date:
            error = 'Fecha de la cita requerido'
        if error is not None:
            flash(error)
        else:
            db, c = get_db()
            c.execute('insert into Cita (created_by,date,doctor,specialization,companion)'
                      ' values (%s,%s,%s,%s,%s)', (g.user['id'], date, doctor, specialization, companion))
        db.commit()
        return redirect(url_for('patrones.index'))

    return render_template('aplicacion/createC.html')
##########################################################################################################################################


@bp.route('/<int:id>/updateC', methods=['GET', 'POST'])
@login_require
def updateC(id):
    cita = get_cita(id)
    if request.method == 'POST':
        date = request.form['fecha_cita']
        doctor = request.form['doctor_cita']
        specialization = request.form['especialidad_cita']
        companion = request.form['acompanante_cita']
        error = None

        if error is not None:
            flash(error)
        else:
            db, c = get_db()
            c.execute('update Cita set date = %s, doctor = %s, specialization = %s, companion = %s'
                      ' where id = %s and created_by = %s', (date, doctor, specialization, companion, id, g.user['id']))
            db.commit()
            return redirect(url_for('patrones.index'))
    return render_template('aplicacion/updateC.html', cita=cita)


def get_cita(id):
    db, c = get_db()
    c.execute('select c.id, c.date, c.doctor, c.created_by, c.specialization, c.companion,'
              ' u.username from Cita c join Usuario u on c.created_by = u.id where c.id = %s', (id,))
    cita = c.fetchone()
    if cita is None:
        abort(404, 'La cita de id {0} no existe'.format(id))
    return cita

##########################################################################################################################################


@bp.route('/<int:id>/deleteC', methods=['POST'])
@login_require
def deleteC(id):
    db, c = get_db()
    c.execute('delete from Cita where id = %s and created_by = %s',
              (id, g.user['id']))
    db.commit()
    return redirect(url_for('patrones.index'))
##########################################################################################################################################


@bp.route('/<string:pagina>')
@login_require
def interfaces(pagina):
    return render_template('aplicacion/{}.html'.format(pagina))

##########################################################################################################################################


@bp.route('/Chat', methods=['GET', 'POST'])
@login_require
def Chat():
    '''
    if request.method=="POST":
        message = request.form['myMessage']

        error = None

        if not message:
            error = 'Mensaje requerido'
        if error is not None:
            flash(error)
        else:
            db, c = get_db()
            c.execute('insert into Mensaje (created_by,Contentmsg)'

                    ' values (%s,%s)',(g.user['id'],message))
        #db.commit()
    mensajes = get_mensaje(g.user['family'])
    notificacion()
    '''

    return render_template('aplicacion/Chat.html')

def get_mensaje(familia):
    db, c = get_db()
    c.execute('select m.id, m.created_by, m.created_at, m.Contentmsg, u.family,'
              ' u.username from Mensaje m join Usuario u on m.created_by = u.id where u.family = %s', (familia,))
    mensaje = c.fetchall()
    if mensaje is None:
        abort(404, 'El mensaje de la familia {0} no existe'.format(familia))
    return mensaje

##########################################################################################################################################


@bp.route('/mensaje')
@login_require
def mensaje():
    db, c = get_db()
    c.execute(
        'select * from usuario where family = "{}"'.format(g.user['family']))
    lista = c.fetchall()

    if len(lista) == 1:
        sendAlert(lista[0]['username'], lista[0]['email'])
    else:
        for usuario in lista:
            sendAlert(usuario['username'], usuario['email'])

    return redirect(url_for('patrones.index'))


def sendAlert(usuario, correo):
    msg = MIMEMultipart()
    message = "¡ALERTA {}! \nAlguien ha utilizado el boton de alerta para notificar a toda la familia de una emergencia.\
        \nPor favor contactate con tus familiares y asegurate que cada uno de ellos se encuentre en buen estado\
        , sobre todo tu(s) adulto(s) mayor(es). No olvides que esta notificación le llega ha todos los usuarios registrados\
        un su familia.".format(usuario)

    password = "patrones12345"
    msg['From'] = "patronesdiseno1@gmail.com"
    msg['To'] = correo
    msg['Subject'] = "¡ALERTA!"

    msg.attach(MIMEText(message, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com: 587')
    server.starttls()
    server.login(msg['From'], password)
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()

##########################################################################################################################################


def notificacion():
    db, c = get_db()
    c.execute(
        'select * from usuario where family = "{}"'.format(g.user['family']))
    lista = c.fetchall()

    if len(lista) != 1:
        for usuario in lista:
            if usuario['id'] != g.user['id']:
                sendNotification(usuario['username'], usuario['email'])


def sendNotification(usuario, correo):
    msg = MIMEMultipart()
    message = "¡{} Nuevo mensaje de {}! \nHay un nuevo mensaje de entrada para la familia.\
        \nPor favor revisa la aplicación para enterarte de las ultimas noticias 🧐.".format(usuario, g.user['username'])

    password = "patrones12345"
    msg['From'] = "patronesdiseno1@gmail.com"
    msg['To'] = correo
    msg['Subject'] = "¡Nuevo mensaje!"

    msg.attach(MIMEText(message, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com: 587')
    server.starttls()
    server.login(msg['From'], password)
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()


########################################################### OBLIGACIONES FINANCIERAS ###########################################################


@bp.route('/Deudas', methods=['GET', 'POST'])
@login_require
def createObF():
    if request.method == "POST":
        name = request.form['nombre_obligacion']
        bank = request.form['Banco_Prestamista ']
        value = request.form['ValorObligacion']
        nextpaydate = request.form['SiguienteFechaDePago']

        error = None

        if not nextpaydate:
            error = 'Fecha de siguiente pago requerido'
        if error is not None:
            flash(error)
        else:
            db, c = get_db()
            c.execute('insert into ObligacionesFinancieras (created_by,name,bank,value,Nextpaydate)'
                      ' values (%s,%s,%s,%s,%s)', (g.user['id'], name, bank, value, nextpaydate))
        db.commit()
        return redirect(url_for('patrones.index'))

    return render_template('aplicacion/Deudas.html')


def get_obligacion(id):
    db, c = get_db()
    c.execute('select o.id, o.name, o.bank, o.value, o.Nextpaydate'
              '  from ObligacionesFinancieras o join Usuario u on o.created_by = u.id where o.id = %s', (id,))
    obligacion = c.fetchone()
    if obligacion is None:
        abort(404, 'ELa obligacion de id {0} no existe'.format(id))
    return obligacion


##########################################################################################################################################

@bp.route('/<int:id>/DeudasM', methods=['GET', 'POST'])
@login_require
def updateD(id):
    obligacion = get_obligacion(id)
    if request.method == 'POST':
        bank = request.form['Banco_Prestamista']
        value = request.form['ValorObligacion']
        nextpaydate = request.form['SiguienteFechaDePago']
        error = None

        if error is not None:
            flash(error)
        else:
            db, c = get_db()
            c.execute('update ObligacionesFinancieras set bank = %s, value = %s, Nextpaydate = %s'
                      ' where id = %s and created_by = %s', (bank, value, nextpaydate, id, g.user['id']))
            db.commit()
            return redirect(url_for('patrones.index'))
    return render_template('aplicacion/DeudasM.html', obligacion=obligacion)


##########################################################################################################################################

@bp.route('/<int:id>/deleteO', methods=['POST'])
@login_require
def deleteO(id):
    db, c = get_db()
    c.execute(
        'delete from ObligacionesFinancieras where id = %s and created_by = %s', (id, g.user['id']))
    db.commit()
    return redirect(url_for('patrones.index'))


##########################################################################################################################################

@bp.route('/Pension')
def Pension():
    db, c = get_db()
    c.execute('select p.id, p.initialvalue, p.startdate, p.pensionvalue from Pension p JOIN Usuario u on '
              'p.created_by = u.id where p.created_by=%s', (g.user['id'],))
    pension = c.fetchone()

    c.execute('select h.id, h.pensionactual, h.expend, h.expendconcept, h.expenddate from historialGastos h JOIN Usuario u on '
              'h.created_by = u.id where h.created_by=%s', (g.user['id'],))
    hpensiones = c.fetchall()

    return render_template('aplicacion/Pension.html',pension=pension, hpensiones=hpensiones)














#########################################----------------INICIAR PENSION

@bp.route('/IniciarPension', methods=['POST'])
def IniciarPension():
    if request.method == "POST":
        initialvalue = request.form['PensionInicial']
        startdate = request.form['FechaPensionInicial']
        pensionvalue = request.form['PensionInicial']

        error = None

        if not initialvalue:
            error = 'Valor inicial de pension requerido'
        if error is not None:
            flash(error)
        else:
            db, c = get_db()
            c.execute('insert into Pension (created_by,initialvalue,startdate,pensionvalue)'
                      ' values (%s,%s,%s,%s)', (g.user['id'], initialvalue, startdate, pensionvalue))
        db.commit()
        return redirect(url_for('patrones.Pension'))

    return render_template('aplicacion/IniciarPension.html')

def deletepension(id):
    db, c = get_db()
    c.execute(
        'delete from Pension where id = %s and created_by = %s', (id, g.user['id']))
    db.commit()


@bp.route('/<int:id>/SumarSaldo', methods=['POST', 'GET'])
def SumarSaldo(id):

    pensioninicial = get_pensioninicial(id)
    pensionactual = get_pensionactual(id)



    if request.method == "POST":
        nuevapension = pensioninicial['initialvalue'] + pensionactual['pensionvalue']
        update_pensionmadre(id,nuevapension)
    
        return redirect(url_for('patrones.Pension'))







    return render_template('aplicacion/SumarSaldo.html', pensioninicial=pensioninicial, pensionactual=pensionactual)

def get_pensioninicial(id):
    db, c = get_db()
    c.execute('select p.id, p.initialvalue'
              '  from Pension p join Usuario u on p.created_by = u.id where p.id = %s', (id,))
    valorpension = c.fetchone()
    if valorpension is None:
        abort(404, 'EL valorpension de id {0} no existe'.format(id))
    return valorpension

def get_pensionactual(id):
    db, c = get_db()
    c.execute('select p.id, p.pensionvalue'
              '  from Pension p join Usuario u on p.created_by = u.id where p.id = %s', (id,))
    valorpension = c.fetchone()
    if valorpension is None:
        abort(404, 'EL valorpension de id {0} no existe'.format(id))
    return valorpension

def update_pensionmadre(id,pensionnueva):

    db, c = get_db()

    c.execute('update Pension set pensionvalue=%s'
                      ' where id = %s and created_by = %s', (pensionnueva, id, g.user['id']))
    db.commit()
    
    


@bp.route('/<int:id>/Gasto', methods=['POST', 'GET'])
def Gasto(id):
    pensionactual = get_pensionactual(id)

    if request.method == "POST":

        concept = request.form['conceptorgasto']
        expend = request.form['valorgasto']
        expenddate = request.form['Fechagasto']

        if pensionactual['pensionvalue']-float(expend) <0:
            error = 'Este gasto lo dejaria sin pensión. No lo haga.'
            flash(error)
        else:
            pensionnueva = pensionactual['pensionvalue']-float(expend)
            update_pensionmadre(id,pensionnueva)
            error = None
            if not expend:

                error = 'Valor del gasto requerido'
            if error is not None:

                flash(error)
            else:

                db, c = get_db()

                c.execute('insert into historialGastos (created_by, pensionactual, expend, expendconcept, expenddate) values (%s,%s,%s,%s,%s)',
                      (g.user['id'], pensionnueva, expend, concept, expenddate))
                db.commit()

        
        
        return redirect(url_for('patrones.Pension'))
    return render_template('aplicacion/Gasto.html', pensionactual=pensionactual)


def get_pensionactual(id):
    db, c = get_db()
    c.execute('select p.id, p.pensionvalue'
              '  from Pension p join Usuario u on p.created_by = u.id where p.id = %s', (id,))
    valorpension = c.fetchone()
    if valorpension is None:
        abort(404, 'EL valorpension de id {0} no existe'.format(id))
    return valorpension

def update_pensionmadre(id,pensionnueva):

    db, c = get_db()

    c.execute('update Pension set pensionvalue=%s'
                      ' where id = %s and created_by = %s', (pensionnueva, id, g.user['id']))
    db.commit()

