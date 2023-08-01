from flask import Flask, render_template, request, redirect, url_for
import pyodbc
from flask import flash
import bcrypt

app = Flask(__name__, static_folder='static')
app.secret_key = "mi_clave_secreta"
connection_string = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=ACERDZ\DIEGO;DATABASE=cafeteria;UID=admDiego;PWD=12345"
def connect_to_database():
    try:
        conn = pyodbc.connect(connection_string)
        return conn
    except pyodbc.Error as e:
        print("Error al conectar a la base de datos:", e)
        return None
    

@app.route('/')
def index():
    connection = connect_to_database()
    if connection:
        try:
            return render_template('index.html')
        except Exception as e:
            return f"Error al ejecutar la consulta: {str(e)}"
    else:
        return "Error de conexión a la base de datos"
    

@app.route('/login', methods=['POST'])
def login():
    connection = connect_to_database()
    Vmatricula = request.form['txtMatricula_login']
    Vpassword = request.form['txtContrasena_login']

    CS = connection.cursor()
    CS.execute("SELECT COUNT(*) FROM tbusuarios WHERE matricula=?", (Vmatricula,))
    userCount = CS.fetchone()[0]
    if userCount == 0:
        flash(f"El usuario {Vmatricula} NO existe", 'error')
        return redirect('/')

    CS.execute("SELECT contrasena, id_tipo_permiso FROM tbusuarios WHERE matricula=?", (Vmatricula,))
    result = CS.fetchone()
    if result:
        conEncriptada = result[0]
        idTipoPermiso = result[1]
        
        if bcrypt.checkpw(Vpassword.encode(), conEncriptada.encode()):
            CS.execute("SELECT nombre FROM tbusuarios WHERE matricula=?", (Vmatricula,))
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
        
        
        connection = connect_to_database()      
        CS = connection.cursor()
        CS.execute('INSERT INTO TbUsuarios (nombre, ap, am, matricula, correo, contrasena) VALUES (?, ?, ?, ?, ?, ?)',
           (Vnombre, VapellidoPaterno, VapellidoMaterno, Vmatricula, VcorreoElectronico, conH))
        CS.connection.commit()
        flash('El usuario se ha agregado correctamente.')
    return redirect(url_for('index'))

def encriptarContrasena(password):
    sal = bcrypt.gensalt()
    conHa = bcrypt.hashpw(password.encode(), sal)
    return conHa


@app.route('/productos')
def menu():
    connection = connect_to_database() 
    cursor = connection.cursor()
    cursor.execute("SELECT p.id_prod, p.nombre, c.nombre, p.descripcion, p.precio, p.disponibilidad, p.stock FROM TbProductos p INNER JOIN tbcategorias c ON p.id_categoria = c.id_categoria")

    QueryMenu = cursor.fetchall()
    cursor.execute("SELECT * FROM tbcategorias")
    QueryCategorias = cursor.fetchall()
    return render_template('adm_products.html', listMenu=QueryMenu, listcategorias=QueryCategorias)

@app.route('/save', methods=['POST'])
def saveProd():
    connection = connect_to_database() 
    if request.method == 'POST':
        #pasamos a variables al contenido de los inputs
        VnombreProd = request.form['txtNombreProd']
        VcategoriaProd = request.form['txtCategoriaProd']
        VdescripcionProd = request.form['txtDescripcionProd']
        VprecioProd = request.form['txtPrecioProd']
        VdisponibilidadProd = request.form['txtDisponibilidadProd']
        VstockProd = request.form['txtStockProd']
        #haremos la conex a la db y ejecutar el insert
        CS = connection.cursor()
        CS.execute('INSERT INTO tbproductos (nombre, id_categoria, descripcion, precio, disponibilidad, stock) VALUES (?, ?, ?, ?, ?, ?)', (VnombreProd, VcategoriaProd, VdescripcionProd, VprecioProd, VdisponibilidadProd, VstockProd))
        connection.commit()
    flash('El producto fue agregado correctamente')
    return redirect(url_for('menu'))

@app.route('/save_category', methods=['POST'])
def saveCategory():
    connection = connect_to_database() 
    if request.method == 'POST':
        # Pasamos a variables al contenido de los inputs
        Vcategoria = str(request.form['txtNombreCategoria'])
        # Haremos la conexión a la base de datos y ejecutar el insert
        CS = connection.cursor()
        CS.execute('INSERT INTO tbcategorias (nombre) VALUES (?)', (Vcategoria,))
        connection.commit()
    flash('La categoría fue agregada correctamente')
    return redirect(url_for('menu'))

@app.route('/edit/<id>')
def edit(id):
    connection = connect_to_database() 
    CS = connection.cursor()
    CS.execute('SELECT p.id_prod ,p.nombre, c.nombre, p.descripcion, p.precio, p.disponibilidad, p.stock from tbproductos p INNER JOIN tbcategorias c on p.id_categoria = c.id_categoria where id_prod= ?',(id,))
    Queryedit = CS.fetchone()
    CS.execute("SELECT * FROM tbcategorias")
    QueryCategoriasedit = CS.fetchall()
    return render_template('adm_editProducts.html',menu = Queryedit, listcategorias=QueryCategoriasedit)

@app.route('/update/<id>', methods=['POST'])
def update(id):
    connection = connect_to_database() 
    if request.method == 'POST':
        txtNombre = request.form['txtNombre']
        txtCategoria = request.form['txtCategoria']
        txtDescripcion = request.form['txtDescripcion']
        txtPrecio = request.form['txtPrecio']
        txtDisponibilidad = request.form['txtDisponibilidad']
        txtStock = request.form['txtStock']
        UpdCur = connection.cursor()
        UpdCur.execute('UPDATE tbproductos SET nombre=?, id_categoria=?, descripcion=?, precio=?, disponibilidad=?, stock=? WHERE id_prod = ?', (txtNombre, txtCategoria, txtDescripcion, txtPrecio, txtDisponibilidad, txtStock, id))
        connection.commit()
    flash('El producto fue actualizado correctamente')
    return redirect(url_for('menu'))

@app.route('/edit2/<id>')
def edit2(id):
    connection = connect_to_database() 
    CS = connection.cursor()
    CS.execute('SELECT p.id_prod ,p.nombre, c.nombre, p.descripcion, p.precio, p.disponibilidad, p.stock from tbproductos p INNER JOIN tbcategorias c on c.id_categoria = c.id_categoria where id_prod = ?',(id,))
    Queryedit = CS.fetchone()
    CS.execute("SELECT * FROM tbcategorias")
    QueryCategoriasedit = CS.fetchall()
    return render_template('adm_deleteProducts.html',menu = Queryedit, listcategorias=QueryCategoriasedit)

@app.route('/delete/<id>', methods=['POST'])
def delete(id):
    connection = connect_to_database() 
    if request.method == 'POST':
        DltCur = connection.cursor()
        DltCur.execute('DELETE FROM tbproductos WHERE id_prod = ?', (id,))
        connection.commit()
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
        
        connection = connect_to_database() 
        CS = connection.cursor()
        CS.execute("SELECT * FROM tbusuarios WHERE matricula=?", (Vmatricula,))
        usuario_existente = CS.fetchone()
        if usuario_existente is not None:
            flash(f"El usuario {Vmatricula} ya existe", 'error')
            return redirect('/agregar-admin')
        else:
            CS.execute('INSERT INTO tbusuarios (nombre, ap, am, matricula, correo, contrasena, id_tipo_permiso) values (?, ?, ?, ?, ?, ?, ?)', (Vnombre, VapellidoPaterno, VapellidoMaterno, Vmatricula, VcorreoElectronico, conH, Vpermiso))
            connection.commit()
            flash('El admin se ha agregado correctamente.')
    return redirect(url_for('addAdm'))

@app.route('/usuarios-penalizados')
def upena():
    return render_template('adm_Upenalizados.html')

@app.route('/cerrar-sesion')
def LogO():
    return render_template('index.html')

@app.route('/usrmenu')
def userMenu():
    connection = connect_to_database() 
    CS = connection.cursor()
    CS.execute("SELECT nombre, descripcion, precio from TbProductos where disponibilidad ='Sí'")
    productos = CS.fetchall()
    return render_template('usr_menu.html',productos=productos)

@app.route('/usrpedidos')
def userp():
    return render_template('usr_pedidos.html')

if __name__ == '__main__':
    app.run(port=5000, debug=True)

