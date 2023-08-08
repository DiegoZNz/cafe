###################################### IMPORTACIONES ####################################################
from flask import Flask, render_template, request, redirect, url_for, session, after_this_request, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
import pyodbc
from flask import flash
import bcrypt
############################# FIN DE LAS IMPORTACIONES #####################################################



######################################## CONECCION CON SQL ################################################################
app = Flask(__name__, static_folder='static')
app.secret_key = "mi_clave_secreta"
#connection_string = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=MSI\BERENICEBARCENAS;DATABASE=cafeteria;UID=twa;PWD=1904"
connection_string = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=ACERDZ\DIEGO;DATABASE=cafeteria;UID=admDiego;PWD=12345"

def connect_to_database():
    try:
        conn = pyodbc.connect(connection_string)
        return conn
    except pyodbc.Error as e:
        print("Error al conectar a la base de datos:", e)
        return None

################################ FIN DE LA CONECCION ####################################################################

################# REDIRECCIONAR  AL LOGIN EN CASO DE QUE NO TENGA UNA CUENTA EXISTENTE #########################

login_manager = LoginManager(app)
login_manager.login_view = 'index'
login_manager.login_message = 'Por favor, inicia sesión para acceder a esta página.' 

################# REDIRECCIONAR  AL LOGIN EN CASO DE QUE NO TENGA UNA CUENTA EXISTENTE #########################



############################### MANEJO DE SECIONES ##############################################################
class User(UserMixin): ###
    def __init__(self, id_usuario, matricula, contrasena):
        self.id = id_usuario
        self.matricula =matricula
        self.pass_hash = contrasena

    def get_id(self):
        return str(self.id)


@login_manager.user_loader
def load_user(user_id):
    connection = connect_to_database()
    cur = connection.cursor()
    cur.execute('SELECT id_usuario, matricula, contrasena FROM TbUsuarios WHERE id_usuario = ?', (user_id,))
    account = cur.fetchone()
    cur.close()

    if account:
        return User(id_usuario=account[0], matricula=account[1], contrasena=account[2])
    return None

PERMISO=0
ID=0
PEDIDO=0



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
  
    if request.method == 'POST' and 'txtMatricula_login' in request.form and 'txtContrasena_login' in request.form:
        _matricula = request.form['txtMatricula_login']
        _password = request.form['txtContrasena_login']

        CS = connection.cursor()
        CS.execute("SELECT id_usuario, matricula, contrasena, id_tipo_permiso FROM TbUsuarios WHERE matricula = ?", (_matricula,))
        account = CS.fetchone()

        if account and bcrypt.checkpw(_password.encode(), account[2].encode()):
            user = User(id_usuario=account[0], matricula=account[1], contrasena=account[2])
            login_user(user)

            global PERMISO
            global ID
            PERMISO = account[3]
            ID = account[0]

            if PERMISO == 1:
                return render_template('adm_dashboard.html')
            else:
                return render_template('usr_menu.html')
        else:
            flash('Usuario o Contraseña Incorrectas')
            return render_template('error.html')
    else:
        flash('Datos de inicio de sesión incompletos')
        return render_template('error.html')
    
####################################### FIN DEL MANEJO DE SECIONES ###############################################################


#####################################  DASHBOARD  #######################################################
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('adm_dashboard.html')


@app.route('/usudashboard')
@login_required
def usudashboard():
    return render_template('usr_dashboard.html')

##################################### FIN  DASHBOARD  #######################################################


############################################# AGREGAR USUARIO ##################################################
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

######################################### FIN AGREGAR USUARIO ##########################################################

######################################### ENCRIPTAR PASSWORD DE  USUARIO ##########################################################

def encriptarContrasena(password):
    sal = bcrypt.gensalt()
    conHa = bcrypt.hashpw(password.encode(), sal)
    return conHa

######################################### FIN ENCRIPTAR PASSWORD DE  USUARIO ##########################################################


########################################################### PRODUCTOS QUE VE EL USUARIO MENU #####################################################


@app.route('/productos')
@login_required
def menu():
    connection = connect_to_database() 
    cursor = connection.cursor()
    cursor.execute("SELECT p.id_prod, p.nombre, c.nombre, p.descripcion, p.precio, p.disponibilidad, p.stock FROM TbProductos p INNER JOIN tbcategorias c ON p.id_categoria = c.id_categoria")

    QueryMenu = cursor.fetchall()
    cursor.execute("SELECT * FROM tbcategorias")
    QueryCategorias = cursor.fetchall()
    return render_template('adm_products.html', listMenu=QueryMenu, listcategorias=QueryCategorias)

@app.route('/save', methods=['POST'])
@login_required
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
@login_required
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
@login_required
def edit(id):
    connection = connect_to_database() 
    CS = connection.cursor()
    CS.execute('SELECT p.id_prod ,p.nombre, c.nombre, p.descripcion, p.precio, p.disponibilidad, p.stock from tbproductos p INNER JOIN tbcategorias c on p.id_categoria = c.id_categoria where id_prod= ?',(id,))
    Queryedit = CS.fetchone()
    CS.execute("SELECT * FROM tbcategorias")
    QueryCategoriasedit = CS.fetchall()
    return render_template('adm_editProducts.html',menu = Queryedit, listcategorias=QueryCategoriasedit)

@app.route('/update/<id>', methods=['POST'])
@login_required
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
@login_required
def edit2(id):
    connection = connect_to_database() 
    CS = connection.cursor()
    CS.execute('SELECT p.id_prod ,p.nombre, c.nombre, p.descripcion, p.precio, p.disponibilidad, p.stock from tbproductos p INNER JOIN tbcategorias c on c.id_categoria = c.id_categoria where id_prod = ?',(id,))
    Queryedit = CS.fetchone()
    CS.execute("SELECT * FROM tbcategorias")
    QueryCategoriasedit = CS.fetchall()
    return render_template('adm_deleteProducts.html',menu = Queryedit, listcategorias=QueryCategoriasedit)

@app.route('/delete/<id>', methods=['POST'])
@login_required
def delete(id):
    connection = connect_to_database() 
    if request.method == 'POST':
        DltCur = connection.cursor()
        DltCur.execute('DELETE FROM tbproductos WHERE id_prod = ?', (id,))
        connection.commit()
    flash('El producto fue eliminado')
    return redirect(url_for('menu'))

########################################### PEDIDOS ##############################################################################

@app.route('/pedidos')
def pedidos():
    connection = connect_to_database()
    cursor = connection.cursor()

    cursor.execute("SELECT p.id_pedido, CONCAT(u.nombre, ' ', u.ap, ' ', u.am), p.fecha_pedido, p.precio_total, ep.tipo FROM TbPedidos p INNER JOIN TbUsuarios u ON p.id_usuario = u.id_usuario INNER JOIN TbEstatusPedido ep ON p.estatus = ep.id_estatuspedido WHERE ep.id_estatuspedido = 1")
    queryped = cursor.fetchall()
    
    cursor.execute("SELECT p.id_pedido, CONCAT(u.nombre, ' ', u.ap, ' ', u.am), p.fecha_pedido, p.precio_total, ep.tipo, u.id_usuario FROM TbPedidos p INNER JOIN TbUsuarios u ON p.id_usuario = u.id_usuario INNER JOIN TbEstatusPedido ep ON p.estatus = ep.id_estatuspedido WHERE ep.id_estatuspedido = 2")
    querypedc = cursor.fetchall()

    cursor.execute("select p.id_pedido, pr.nombre, dp.cantidad, pr.precio from TbDetallepedidos dp inner join TbPedidos p on dp.id_pedido = p.id_pedido inner join TbProductos pr on dp.id_producto = pr.id_prod")
    querypedp = cursor.fetchall()
    print (queryped)
    
    cursor.close()
    return render_template('pedidos.html', listPedidos=queryped,listPedidosc=querypedc, listdp=querypedp)

@app.route('/cambio-estatus/<id>') #CAMBIA EL ESTATUS DE PENDIENTE A EN PROCESO
def cambio_estatus(id):
    connection = connect_to_database()
    cursor = connection.cursor()
    cursor.execute("EXEC sp_cambioEstatusEP @pedido_id=?", (id,))
    connection.commit()
    cursor.close()
    return redirect('/pedidos')


@app.route('/cambio-estatusC/<id>') #CAMBIA EL ESTATUS DE EN PROCESO A COMPLETADO
def cambio_estatusC(id):
    connection = connect_to_database()
    cursor = connection.cursor()
    cursor.execute("EXEC sp_cambioEstatusC ?", (id,))
    connection.commit()
    cursor.close()

    return redirect('/pedidos')

@app.route('/penalizarusu/<id>') #AGREGAR PENALIZACION y cambiar el estatus del pedido a cancelado
def penalizarusu(id):
    connection = connect_to_database()
    cursor = connection.cursor()
    cursor.execute("EXEC sp_agregarPenalizacion ?", (id,))
    connection.commit()
    cursor.close()

    return redirect('/pedidos')
   
########################################### FIN DE PEDIDOS ##############################################################################

########################################################### PRODUCTOS QUE VE EL USUARIO MENU #####################################################

######################################### AGREGAR ADMINSTRADOR ####################################################################
@app.route('/agregar-admin')
@login_required
def addAdm():

    connection = connect_to_database() 
    cursor = connection.cursor()
    cursor.execute("SELECT u.nombre, u.ap, u.am, u.matricula, u.correo, p.permiso, u.estatus FROM TbUsuarios u INNER JOIN TbRoles p ON p.id_tipo_permiso = u.id_tipo_permiso  WHERE u.id_tipo_permiso = 1")
    QueryUsuario = cursor.fetchall()
    # Convertir el valor numérico del estatus a "Activo" si es igual a 1
    for usuario in QueryUsuario:
        if usuario[6] == 1:
            usuario[6] = "Activo"
            
    return render_template('adm_admin.html', listUsuario=QueryUsuario)

@app.route('/save-adm', methods=['POST'])
@login_required
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
#########################################FIN DE  AGREGAR ADMINSTRADOR ####################################################################

############################################# USUARIOS PENALIZADOS ####################################################################

@app.route('/usuarios-penalizados')
@login_required
def upena():
    
    connection = connect_to_database() 
    cursor = connection.cursor()
    cursor.execute("SELECT u.matricula, CONCAT(u.nombre,' ',u.am,' ', u.ap), p.fecha_penalizacion, u.estatus, u.id_usuario FROM TbPenalizaciones p INNER JOIN TbUsuarios u ON u.id_usuario=p.id_usuario WHERE u.id_tipo_permiso=2 AND u.estatus=0")
    QueryPenalizacion = cursor.fetchall()
      # Reemplazar valores de estatus numéricos por "Activo" o "Desactivado"
    for penalizacion in QueryPenalizacion:
        if penalizacion[3] == 1:
            penalizacion[3] = "Activo"
        elif penalizacion[3] == 0:
            penalizacion[3] = "Desactivado"            
    return render_template('adm_Upenalizados.html', listPenalizacion=QueryPenalizacion)

@app.route('/reactivar/<id>') #REACTIVAR USUARIO
def reactivar(id):
    connection = connect_to_database()
    cursor = connection.cursor()
    cursor.execute("EXEC sp_cambiarEstatusUsuario ?", (id,))
    connection.commit()
    cursor.close()

    return redirect('/usuarios-penalizados')
   

############################################# FIN USUARIOS PENALIZADOS ####################################################################


#################################### CERRAR SESION ########################################################
@app.route('/logout')
@login_required
def logout():
    @after_this_request
    def add_no_cache(response):
        response.headers['Cache-Control'] = 'no-store'
        return response

    logout_user()
    return redirect(url_for('index'))
#################################### CERRAR SESION ########################################################

############################################# MENU USUARIOS ####################################################################

@app.route('/usrmenu')
@login_required
def userMenu():
    connection = connect_to_database() 
    CS = connection.cursor()
    CS.execute("SELECT id_prod, nombre, descripcion, precio from TbProductos where disponibilidad ='Sí'")
    productos = CS.fetchall()
    return render_template('usr_menu.html',productos=productos)

############################################# FIN MENU USUARIOS ####################################################################


@app.route('/usrpedidos')
@login_required
def userp():
    return render_template('usr_pedidos.html')


@app.route('/guardar_precio_total', methods=['POST'])
def guardar_precio_total():
    
    try:
        data = request.get_json()
        precio_total = data['precioTotal']
        connection = connect_to_database() 
        CS = connection.cursor()
        # Utiliza el valor de la variable global ID para obtener el usuario_id del usuario con sesión activa
        usuario_id = ID
        CS.execute('INSERT INTO TbPedidos (fecha_pedido, id_usuario, precio_total) VALUES (GETDATE(), ?, ?)', (usuario_id, precio_total))
        connection.commit()
        return jsonify({"message": "Precio total guardado en la base de datos"})

    except Exception as e:
        CS.rollback()
        return jsonify({"error": "Error al guardar el precio total en la base de datos: " + str(e)})
    
    


    
@app.route('/guardar_detalles_pedido', methods=['POST'])
def guardar_detalles_pedido():
    global PEDIDO
    connection = connect_to_database() 
    CS = connection.cursor()
    CS.execute('SELECT COUNT(*) FROM TbPedidos')
    dbpedido=CS.fetchone()
    
    PEDIDO = dbpedido[0]
    print("Pedido actual",PEDIDO)
    print ("/---------------------/",PEDIDO)
    idpedido = PEDIDO
    detalles = request.json.get('detallesProductos')
    print("Detalles a insertar:", detalles)  # Imprime la lista de detalles para verificar
    
    for detalle in detalles:
        # Convertir los valores a números enteros o de punto flotante
        
        id_producto = int(detalle['id'])
        cantidad = int(detalle['cantidad'])
        precio = float(detalle['precio'])
        print (idpedido,id_producto,cantidad,precio)
        # Insertar detalles del pedido en la tabla de Detalles de Pedido
        CS.execute("INSERT INTO TbDetallepedidos (id_pedido, id_producto, cantidad, precio_uni) VALUES (?, ?, ?, ?)", idpedido, id_producto, cantidad, precio)
        
    CS.commit()
    return jsonify({'message': 'Detalles de productos recibidos y guardados'})




############################################# PUERTO  ####################################################################

if __name__ == '__main__':
    app.run(port=5000, debug=True)

############################################# PUERTO  ####################################################################
