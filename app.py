from crypt import methods
from distutils.util import execute
from flask import Flask
from flask import render_template, request, redirect, url_for, flash
from flaskext.mysql import MySQL
#Para mostrar la foto en el index.html
from flask import send_from_directory
from datetime import datetime
#Para acceder a modificar la foto debemos importar una libreria del SO
import os

app = Flask(__name__)
#Agregar una llave secreta por la info que se maneja
app.secret_key="Develoteca"

mysql = MySQL()
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='sistema'
mysql.init_app(app)

#Crear una referencia a esa carpeta utilizando funcionalidades del SO
CARPETA = os.path.join('uploads')
#Guardamos la ruta como una carpeta
app.config['CARPETA'] = CARPETA

#Crear acceso url
@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'],nombreFoto)

@app.route('/')
def index():

    sql = "select * from empleados;"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    empleados = cursor.fetchall()
    print(empleados)
    conn.commit()

    return render_template('empleados/index.html', empleados = empleados)

@app.route('/destroy/<int:id>')
def destroy(id):
    conn = mysql.connect()
    cursor = conn.cursor()

    #Borrar la Foto de la carpeta
    cursor.execute("select foto from empleados where id = %s",id)
    fila = cursor.fetchall()
    os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))

    cursor.execute("delete from empleados where id = %s",(id))
    conn.commit()
    return redirect('/')

@app.route('/edit/<int:id>')
def edit(id):

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("select * from empleados where id = %s",(id))
    empleados = cursor.fetchall()
    
    conn.commit()

    return render_template('empleados/edit.html', empleados = empleados)

@app.route('/update', methods=['POST'])
def update():
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']
    id = request.form['txtID']
    
    sql = "update empleados set nombre = %s, correo = %s where id = %s;"

    datos = (_nombre, _correo, id)
    
    conn = mysql.connect()
    cursor = conn.cursor()
    
    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    if _foto.filename != '':
        nuevoNombreFoto = tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)

        #Ejecutar un cursor para recuperar los datos de la foto
        cursor.execute("select foto from empleados where id = %s",id)
        fila = cursor.fetchall()

        os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))
        cursor.execute("update empleados set foto=%s where id=%s",(nuevoNombreFoto,id))
        conn.commit()

    cursor.execute(sql, datos)
    conn.commit()

    return redirect('/')

@app.route('/create')
def create():
    return render_template('empleados/create.html')

@app.route('/store', methods=['POST'])
def storage():
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']

    if _nombre == '' or _correo == '' or _foto == '':
        flash('Recuerda llenar los datos de los campos')
        return redirect(url_for('create'))


    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")
    if _foto.filename != '':
        nuevoNombreFoto = tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)

    sql = "insert into empleados(nombre, correo, foto) values(%s, %s,%s);"
    datos = (_nombre, _correo, nuevoNombreFoto)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()

    return redirect('/')

if __name__=='__main__':
    app.run(port=3000,debug=True)