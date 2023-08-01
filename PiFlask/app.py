from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from flask import flash
import bcrypt

app = Flask(__name__, static_folder='static')
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_cafeteria'
mysql = MySQL(app)
app.secret_key = "mi_clave_secreta"

@app.route('/')
def index():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()

        if result:
            return render_template('index.html')
        else:
            return "No se pudo conectar a la base de datos"
    except Exception as e:
        return f"Error de conexión a la base de datos: {str(e)}" 

@app.route('/login', methods=['POST'])
def login():
    Vmatricula = request.form['txtMatricula_login']
    Vpassword = request.form['txtContrasena_login']

    CS = mysql.connection.cursor()
    CS.execute("SELECT COUNT(*) FROM tbusuarios WHERE matricula=%s", (Vmatricula,))
    userCount = CS.fetchone()[0]
    if userCount == 0:
        flash(f"El usuario {Vmatricula} NO existe", 'error')
        return redirect('/')

    CS.execute("SELECT contrasena, id_tipo_permiso FROM tbusuarios WHERE matricula=%s", (Vmatricula,))
    result = CS.fetchone()
    if result:
        conEncriptada = result[0]
        idTipoPermiso = result[1]
        
        if bcrypt.checkpw(Vpassword.encode(), conEncriptada.encode()):
            CS.execute("SELECT nombre FROM tbusuarios WHERE matricula=%s", (Vmatricula,))
            nombre = CS.fetchone()[0]
            flash(f'Bienvenido {nombre}!')

            if idTipoPermiso == 1:
                return redirect('/productos')  # Ruta del administrador
            elif idTipoPermiso == 2:
                return redirect('/usrmenu')  # Ruta del cliente
        else:
            flash("Contraseña incorrecta", 'error')
    else:
        flash("Error al obtener datos del usuario", 'error')
    return redirect(url_for('index'))

@app.route('/guardar', methods=['POST'])
def guardar():
    if request.method == 'POST':
        Vnombre = request.form['txtNombre_guardar']
        VapellidoPaterno = request.form['txtApellidoPaterno_guardar']
        VapellidoMaterno = request.form['txtApellidoMaterno_guardar']
        Vmatricula = request.form['txtMatricula_guardar']
        VcorreoElectronico = request.form['txtCorreoElectronico_guardar']
        Vcontrasena = request.form['txtContrasena_guardar'] 
        
        conH=encriptarContrasena(Vcontrasena)
        
        CS = mysql.connection.cursor()
        CS.execute("SELECT * FROM tbusuarios WHERE matricula=%s", (Vmatricula,))
        usuario_existente = CS.fetchone()
        if usuario_existente is not None:
            flash(f"El usuario {Vmatricula} ya existe", 'error')
            return redirect('/login')
        else:
            CS.execute('INSERT INTO tbusuarios (nombre, ap, am, matricula, correo, contrasena) values (%s, %s, %s, %s, %s, %s)', (Vnombre, VapellidoPaterno, VapellidoMaterno, Vmatricula, VcorreoElectronico, conH))
            mysql.connection.commit()
            flash('El usuario se ha agregado correctamente.')
    return redirect(url_for('index'))

def encriptarContrasena(password):
    sal = bcrypt.gensalt()
    conHa = bcrypt.hashpw(password.encode(), sal)
    return conHa

@app.route('/productos')
def menu():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT p.`id_product` ,p.nombre, c.nombre, p.`descripcion`, p.`precio`, p.`disponibilidad`, p.stock from tbproductos p INNER JOIN tbcategorias c on id_categoria = c.id_categoría")
    QueryMenu = cursor.fetchall()
    cursor.execute("SELECT * FROM tbcategorias")
    QueryCategorias = cursor.fetchall()
    return render_template('adm_products.html', listMenu=QueryMenu, listcategorias=QueryCategorias)

@app.route('/save', methods=['POST'])
def saveProd():
    if request.method == 'POST':
        #pasamos a variables al contenido de los inputs
        VnombreProd = request.form['txtNombreProd']
        VcategoriaProd = request.form['txtCategoriaProd']
        VdescripcionProd = request.form['txtDescripcionProd']
        VprecioProd = request.form['txtPrecioProd']
        VdisponibilidadProd = request.form['txtDisponibilidadProd']
        VstockProd = request.form['txtStockProd']
        #haremos la conex a la db y ejecutar el insert
        CS = mysql.connection.cursor()
        CS.execute('INSERT INTO tbproductos (nombre, id_categoria, descripcion, precio, disponibilidad, stock) VALUES (%s, %s, %s, %s, %s, %s)', (VnombreProd, VcategoriaProd, VdescripcionProd, VprecioProd, VdisponibilidadProd, VstockProd))
        mysql.connection.commit()
    flash('El producto fue agregado correctamente')
    return redirect(url_for('menu'))


@app.route('/save_category', methods=['POST'])
def saveCategory():
    if request.method == 'POST':
        # Pasamos a variables al contenido de los inputs
        Vcategoria = str(request.form['txtNombreCategoria'])
        # Haremos la conexión a la base de datos y ejecutar el insert
        CS = mysql.connection.cursor()
        CS.execute('INSERT INTO tbcategorias (nombre) VALUES (%s)', (Vcategoria,))
        mysql.connection.commit()
    flash('La categoría fue agregada correctamente')
    return redirect(url_for('menu'))

@app.route('/edit/<id>')
def edit(id):
    CS = mysql.connection.cursor()
    CS.execute('SELECT p.`id_product` ,p.nombre, c.nombre, p.`descripcion`, p.`precio`, p.`disponibilidad`, p.stock from tbproductos p INNER JOIN tbcategorias c on id_categoria = c.id_categoría where id_product = %s',(id,))
    Queryedit = CS.fetchone()
    CS.execute("SELECT * FROM tbcategorias")
    QueryCategoriasedit = CS.fetchall()
    return render_template('adm_editProducts.html',menu = Queryedit, listcategorias=QueryCategoriasedit)


@app.route('/update/<id>', methods=['POST'])
def update(id):
    if request.method == 'POST':
        txtNombre = request.form['txtNombre']
        txtCategoria = request.form['txtCategoria']
        txtDescripcion = request.form['txtDescripcion']
        txtPrecio = request.form['txtPrecio']
        txtDisponibilidad = request.form['txtDisponibilidad']
        txtStock = request.form['txtStock']
        UpdCur = mysql.connection.cursor()
        UpdCur.execute('UPDATE tbproductos SET nombre=%s, id_categoria=%s, descripcion=%s, precio=%s, disponibilidad=%s, stock=%s WHERE id_product = %s', (txtNombre, txtCategoria, txtDescripcion, txtPrecio, txtDisponibilidad, txtStock, id))
        mysql.connection.commit()
    flash('El producto fue actualizado correctamente')
    return redirect(url_for('menu'))


@app.route('/edit2/<id>')
def edit2(id):
    CS = mysql.connection.cursor()
    CS.execute('SELECT p.`id_product` ,p.nombre, c.nombre, p.`descripcion`, p.`precio`, p.`disponibilidad`, p.stock from tbproductos p INNER JOIN tbcategorias c on id_categoria = c.id_categoría where id_product = %s',(id,))
    Queryedit = CS.fetchone()
    CS.execute("SELECT * FROM tbcategorias")
    QueryCategoriasedit = CS.fetchall()
    return render_template('adm_deleteProducts.html',menu = Queryedit, listcategorias=QueryCategoriasedit)


@app.route('/delete/<id>', methods=['POST'])
def delete(id):
    if request.method == 'POST':
        DltCur = mysql.connection.cursor()
        DltCur.execute('DELETE FROM tbproductos WHERE id_product = %s', (id,))
        mysql.connection.commit()
    flash('El producto fue eliminado')
    return redirect(url_for('menu'))

@app.route('/pedidos')
def pedidos():
    return render_template('pedidos.html')

@app.route('/agregar-admin')
def addAdm():
    return render_template('adm_addAdm.html')

@app.route('/save-adm', methods=['POST'])
def saveAdm():
    if request.method == 'POST':
        Vnombre = request.form['txtnombre']
        VapellidoPaterno = request.form['txtappaterno']
        VapellidoMaterno = request.form['txtapmaterno']
        Vmatricula = request.form['txtmatricula']
        VcorreoElectronico = request.form['txtcorreo']
        Vcontrasena = request.form['txtcontrasena'] 
        Vpermiso = 1
        
        conH=encriptarContrasena(Vcontrasena)
        
        
        CS = mysql.connection.cursor()
        CS.execute("SELECT * FROM tbusuarios WHERE matricula=%s", (Vmatricula,))
        usuario_existente = CS.fetchone()
        if usuario_existente is not None:
            flash(f"El usuario {Vmatricula} ya existe", 'error')
            return redirect('/agregar-admin')
        else:
            CS.execute('INSERT INTO tbusuarios (nombre, ap, am, matricula, correo, contrasena, id_tipo_permiso) values (%s, %s, %s, %s, %s, %s, %s)', (Vnombre, VapellidoPaterno, VapellidoMaterno, Vmatricula, VcorreoElectronico, conH, Vpermiso))
            mysql.connection.commit()
            flash('El admin se ha agregado correctamente.')
    return redirect(url_for('addAdm'))

@app.route('/usuarios-penalizados')
def upena():
    return render_template('adm_Upenalizados.html')

@app.route('/cerrar-sesion')
def LogO():
    return render_template('index.html')

@app.route('/usrmenu')
def userp():
    return render_template('usr_menu.html')

@app.route('/usrpedidos')
def userMenu():
    return render_template('usr_pedidos.html')

if __name__ == '__main__':
    app.run(port=7000, debug=True)
