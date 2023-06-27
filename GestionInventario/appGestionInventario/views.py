from django.shortcuts import render, redirect
from django.db import Error, transaction
from django.contrib.auth.models import *
from appGestionInventario.models import *
from django.contrib.auth import authenticate, logout
from django.contrib import auth
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
import threading
from smtplib import SMTPException
from django.http import JsonResponse
import random
import string, os, urllib, json


# Create your views here.

def generarPassword():

    longitud = 10
    caracteres = string.ascii_lowercase + string.ascii_uppercase \
                 + string.digits + string.punctuation
    password = ''
    for i in  range(longitud):
        password += ''.join(random.choice(caracteres))
    return password

def registrarUsuario(request):
    try:
        nombre = request.POST["txtNombre"]
        apellido = request.POST["txtApellido"]
        correo = request.POST["txtCorreo"]
        tipo = request.POST["cbTipo"]
        foto = request.FILES.get("Fimagen", None)
        idRol = int(request.POST["cbRol"])
        with transaction.atomic():
            #crear un objeto de tipo user 
            user = User(username=correo, first_name=nombre,
                        last_name=apellido, email=correo,
                        userTipo=tipo, userFoto=foto)
            user.save()
            #obtener el rol de acuerdo a id del rol
            rol = Group.objects.get(pk=idRol)
            #agregar el usuario a ese Rol
            user.groups.add(rol)
            #si el rol es administrativo se habilita para que tenga acceso
            #al sitio web del administrador
            if(rol.name=="Administrador"):user.is_staff = True
            #guardamos el usuario con lo que tenemos
            user.save()
            #llamamos a la funcion generalPassword
            passwordGenerado = generarPassword()
            print(f"password {passwordGenerado}")
            #con el usuario creado llamamos a la funcion set_password que
            #encripta el password y lo agrega al campo password del user
            user.set_password(passwordGenerado)
            #se actualiza el user
            user.save()
            mensaje = "usuario agregado correctamente"
            retorno = {"mensaje":mensaje}
            # Enviar correo cliente
            asunto = 'Registro en nuestro Sistema CIES-NEIVA'
            mensaje = f'Cordial Saludo, <b>{user.first_name} {user.last_name}</b>, nos permitimos \
                informarle que usted ha sido registrado en nuestro Sistema de Gestión de Inventario \
                del Centro de la Industria, la Empresa y los Servicios CIES de la ciudad de Neiva. \
                Sus datos para ingresar a nuestro sistema son los siguientes:<br> \
                <br><b>Username: </b> {user.username} \
                <br><b>Password: </b> {passwordGenerado} \
                <br><br>Lo invitamos a ingresar a nuestro sistema mediante el siguiente link: \
                https://gestioninventario.sena.edu.co'
            thread = threading.Thread(target=enviarCorreo,
                                    args=(asunto,mensaje,[user.email]))
            thread.start()
            #enviar correo al ususario
            return redirect("/vistagestionarUsuario/",retorno)
    except Error as error:
        transaction.rollBack()
        mensaje = f"{error}"
    retorno = {"mensaje": mensaje, "user": user}
    return render(request, "administrador/registrarUsuario.html", retorno)

def vistaRegistrarUsuario(request):
    if request.user.is_authenticated:
        roles = Group.objects.all()
        tipos = tipoUsuario
        retorno = {"roles":roles,"user":None, "tipoUsuario":tipos}
        return render(request, "administrador/registrarUsuario.html", retorno)
    else:
        mensaje = "Debe Iniciar Sesion"
        return render(request,"iniciarSesion.html",{"mensaje":mensaje})

def inicio(request):
    return render(request, "inicio.html")

def listaUsuarios(request):
    if request.user.is_authenticated:
        try:
            usuario = User.objects.all()
            mensaje = ""
            retorno = {"mensaje": mensaje, "listaUsuarios":usuario}
            return render(request,"administrador/gestionarUsuarios.html", retorno)
        except Error as error:
            mensaje = "Debe iniciar Sesion"
            return render(request, "iniciarSesion.html",{"mensaje":mensaje})
    else:
        mensaje = "Debe Iniciar Sesion"
        return render(request,"iniciarSesion.html",{"mensaje":mensaje})

def consultarUsuario(request, id):
    try:
        usuario = User.objects.get(id=id)
        tipos =tipoUsuario
        roles = Group.objects.all()
        mensaje = ""
    except Error as error:
        mensaje = f"Problemas {error}"
    retorno = {"mensaje": mensaje, "usuario": usuario, "tipoUsuario": tipos,"roles": roles}
    return render(request, "administrador/editarUsuario.html", retorno)

def actualizarUsuario(request):
    idUsuario = int(request.POST["id"])
    nombre = request.POST["txtNombre"]
    apellido = request.POST["txtApellido"]
    correo = request.POST["txtCorreo"]
    tipo = request.POST["cbTipo"]
    foto = request.FILES.get("Fimagen", False)
    try:
        usuario = User.objects.get(id=idUsuario)
        usuario.first_name = nombre
        usuario.last_name = apellido
        usuario.email = correo
        usuario.userTipo = tipo
        if(foto):
            usuario.userFoto  = foto
        else:
            usuario.userFoto = usuario.userFoto
        usuario.save()
        mensaje  = "Usuario actualizado correctamente"
        return redirect("/vistagestionarUsuario/")
    except Error as error:
        mensaje = f"Problemas al realizar el proceso de actualizar el usuario {error}"
    rol = Group.objects.all()
    retorno = {"mensaje":mensaje, "roles":rol, "usuario": usuario}
    return render (request, "administrador/editarUsuario.html", retorno)

def eliminarUsuario(request, id):
    try: 
        usuario = User.objects.get(id=id)
        if usuario.userFoto:
            imagen = usuario.userFoto.path
            if os.path.exists(imagen):
                os.remove(imagen)
        usuario.delete()
        mensaje="Usuario eliminado correctamente"
    except Error as error:
        mensaje=f"problemas al eliminar el usuario {error}"

    retorno = {"mensaje":mensaje}
    return redirect("/vistagestionarUsuario/", retorno)

# def vistaLogin(request):
#     return render(request, "iniciarSesion.html")

def login(request):
    # Validar el recaptcha 
    ''' Begin reCAPTCHA validation'''
    recaptcha_response = request.POST.get('g-recaptcha-response')
    url = 'https://www.google.com/recaptcha/api/siteverify'
    values = {
        'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
        'response': recaptcha_response
    }
    data = urllib.parse.urlencode(values).encode()
    req = urllib.request.Request(url, data=data)
    response = urllib.request.urlopen(req)
    result = json.loads(response.read().decode())
    print(result)
    ''' End reCAPTCHA validation'''
    
    if result['success']:
        username = request.POST["txtUsername"]
        password = request.POST["txtPassword"]
        user = authenticate(username=username, password=password)
        if user is not None:
            # Registrar la variable de sesión
            auth.login(request,user)
            if user.groups.filter(name='Administrador').exists():
                return redirect ('/inicioAdministrador')
            elif user.groups.filter(name='Asistente').exists():
                return redirect('/inicioAsistente')
            else:
                return redirect('/inicioInstructor')
        else:
            mensaje = "Usuario o Contraseña Incorrectas"
            return render(request,"iniciarSesion.html",{"mensaje":mensaje})
    else: 
        mensaje = "Debe validar primero el recaptcha"
        return render(request,"iniciarSesion.html",{"mensaje":mensaje})
    
def inicioAdministrador(request):
    if request.user.groups.filter(name='Administrador').exists():
        usuario = request.user
        retorno = {"usuario": usuario}
        return render(request, "administrador/inicio.html", retorno)
    else:
        mensaje = "Debe iniciar sesión"
        retorno = {"mensaje": mensaje}
        return render(request, 'iniciarSesion.html', retorno)

def inicioAsistente(request):
    if request.user.groups.filter(name='Asistente').exists():
        usuario = request.user
        retorno = {"usuario": usuario}
        return render(request, "asistente/inicio.html", retorno)
    else:
        mensaje = "Debe iniciar sesión"
        retorno = {"mensaje": mensaje}
        return render(request, 'iniciarSesion.html', retorno)
    
def inicioInstructor(request):
    if request.user.groups.filter(name='Instructor').exists():
        usuario = request.user
        retorno = {"usuario": usuario}
        return render(request, "instructor/inicio.html", retorno)
    else:
        mensaje = "Debe iniciar sesión"
        retorno = {"mensaje": mensaje}
        return render(request, 'iniciarSesion.html', retorno)
    
def enviarCorreo(asunto=None,mensaje=None,destinatario=None):
    remitente = settings.EMAIL_HOST_USER
    template = get_template('enviarCorreo.html')
    contenido = template.render({
        'destinatario':destinatario,
        'mensaje':mensaje,
        'asunto':asunto,
        'remitente':remitente
    })
    try:
        correo = EmailMultiAlternatives(asunto,mensaje,remitente,destinatario)
        correo.attach_alternative(contenido, 'text/html')
        correo.send(fail_silently=True)
    except SMTPException as error:
        print(error)

def vistagestionarDevolutivo(request):
    if request.user.is_authenticated:
        elementosDevolutivos = Devolutivo.objects.all()
        retorno = {"listaElementosDevolutivos": elementosDevolutivos}
        return render(request,"asistente/gestionarDevolutivo.html", retorno)
    else:
        mensaje = "Debe Iniciar Sesion"
        return render(request,"iniciarSesion.html",{"mensaje":mensaje})
    
def vistaRegistrarDevolutivo(request):
    if request.user.is_authenticated:
        retorno = {"tipoElemento":tipoElemento, "estados": estadosElementos, "depositos":ubicacionDeposito }
        return render(request, "asistente/registrarDevolutivo.html", retorno)
    else:
        mensaje = "Debe Iniciar Sesion"
        return render(request,"iniciarSesion.html",{"mensaje":mensaje})

def registrarDevolutivo(request):
    estado = False
    try:
        placaSena = request.POST["txtPlacaSena"]
        fechaInventario = request.POST["txtFechaSena"]
        tipoElemento = request.POST["cbTipoEle"]
        serial = request.POST.get("txtSerial", None)
        marca = request.POST.get("txtMarca", None)
        valorUnitario = int(request.POST["txtValor"])
        estado = request.POST["cbEstado"]
        nombre = request.POST["txtNombre"]
        descripcion = request.POST["txtDescripcion"]
        deposito = request.POST["cbDeposito"]
        estante = request.POST.get("numEstante",None)
        entrePano = request.POST.get("numEntrepano", None)
        locker = request.POST.get("numLocker",None)
        archivo = request.FILES.get("FimagenDev", None)
        with transaction.atomic():
            # Obtener cuantos elementos se han registrado
            cantidad = Elemento.objects.all().count()
            # Crear un codigo a partir de la cantidad ajustando el inicio
            codigoElemento = tipoElemento.upper() + str(cantidad+1).rjust(6,'0')
            # Crear el elemento
            elemento = Elemento(eleCodigo = codigoElemento,eleNombre = nombre, eleTipo = tipoElemento, 
                                eleEstado = estado)
            # Guardar el elemento en la base de datos
            elemento.save()
            # Crear objeto ubicacion fisica del elemento
            ubicacion = UbicacionFisica(ubiDeposito=deposito,ubiEstante=estante,ubiEntrepano=entrePano,ubiLocker=locker,ubiElemento=elemento)
            # Registrar en la base de datos la ubicacion fisica del elemento
            ubicacion.save()
            # Crear el devolutivo
            elementoDevolutivo = Devolutivo(devPlacaSena=placaSena,devSerial=serial,
                                            devDescripcion=descripcion,devMarca=marca,
                                            devFechaIngresoSENA=fechaInventario,
                                            devValor=valorUnitario,devFoto=archivo,
                                            devElemento=elemento, devUbicacion=ubicacion)
            elementoDevolutivo.save()
            estado = True
            mensaje = f'Elemento Devolutivo registrado satisfactoriamente con el codigo {codigoElemento}'
    except Error as error:
        transaction.rollback()
        mensaje = "Error"
    retorno = {"mensaje":mensaje,"devolutivo":elementoDevolutivo,"estado":estado}
    return render (request,"asistente/registrarDevolutivo.html",retorno)

def consultarDevolutivo(request, id, idUbi, idDevo):
    try:
        elemento = Elemento.objects.get(id=id)
        ubicacion = UbicacionFisica.objects.get(id=idUbi)
        devolu = Devolutivo.objects.get(id=idDevo)
        tiposEle =tipoElemento
        estados = estadosElementos
        ubicacionFis = ubicacionDeposito
        mensaje = ""
        fecha_sena = devolu.devFechaIngresoSENA.strftime('%Y-%m-%d')
        valorEntero = int(devolu.devValor)
    except Error as error:
        mensaje = f"Problemas {error}"
    retorno = {"mensaje": mensaje, "elemento": elemento,"ubicacion":ubicacion ,"devolutivo":devolu,"tiposEle": tiposEle, "estados": estados, "depositos":ubicacionFis, "fecha_sena": fecha_sena, "valorEntero": valorEntero}
    return render(request, "asistente/editarDevolutivo.html", retorno)

def actualizarDevolutivo(request):
    idElemento = int(request.POST["id"])
    idUbicacion = int(request.POST["idUbi"])
    idDevolutivo = int(request.POST["idDevo"])
    placaSena = request.POST["txtPlacaSena"]
    fechaInventario = request.POST["txtFechaSena"]
    tipoElemento = request.POST["cbTipoEle"]
    serial = request.POST.get("txtSerial", False)
    marca = request.POST.get("txtMarca", False)
    valor = float(request.POST["txtValor"])
    estado = request.POST["cbEstado"]
    nombre = request.POST["txtNombre"]
    descripcion = request.POST["txtDescripcion"]
    deposito = request.POST["cbDeposito"]
    estante = request.POST.get("numEstante",False)
    entrePano = request.POST.get("numEntrepano", False)
    locker = request.POST.get("numLocker",False)
    archivo = request.FILES.get("Fimagen", False)
    try:
        elemento = Elemento.objects.get(id=idElemento)
        cantidad = Elemento.objects.all().count()
        codigo = tipoElemento.upper() + str(cantidad+1).rjust(6,'0')
        elemento.eleCodigo = codigo
        elemento.eleNombre = nombre
        elemento.eleTipo = tipoElemento
        elemento.eleEstado = estado
        elemento.save()
        # Se empieza a manejar la ubicacion de acuerdo a lo guardado
        ubicacion = UbicacionFisica.objects.get(id=idUbicacion)
        ubicacion.ubiDeposito = deposito
        ubicacion.ubiEstante = estante
        ubicacion.ubiEntrepano = entrePano
        ubicacion.ubiLocker = locker
        ubicacion.ubiElemento = elemento
        ubicacion.save()
        #Se empieza a manejar el devolutivo de acuerdo a lo guardado
        eleDevolu = Devolutivo.objects.get(id=idDevolutivo)
        eleDevolu.devPlacaSena = placaSena
        eleDevolu.devSerial = serial
        eleDevolu.devDescripcion = descripcion
        eleDevolu.devMarca = marca
        eleDevolu.devFechaIngresoSENA = fechaInventario
        eleDevolu.devValor = valor
        eleDevolu.devElemento = elemento
        eleDevolu.devUbicacion = ubicacion
        if(archivo):
            eleDevolu.devFoto  = archivo
        else:
            eleDevolu.devFoto = eleDevolu.devFoto
        eleDevolu.save()
        mensaje  = "Elemento actualizado correctamente"
        return redirect("/vistagestionarDevolutivo/")
    except Error as error:
        mensaje = f"Problemas al realizar el proceso de actualizar el elemento {error}"
    retorno = {"mensaje":mensaje, "elemento": eleDevolu }
    return render (request, "asistente/editarDevolutivo.html", retorno)

def cerrarSesion(request):
    logout(request)
    return redirect('/inicioSesion/')

def vistaRegistrarMaterial(request):
    unidadMed = UnidadMedida.objects.all()
    retorno = {"unidadMed": unidadMed, "estados": estadosElementos, "depositos": ubicacionDeposito}
    return render (request, "asistente/registrarMaterial.html", retorno)

def registrarMaterial(request):
    estado = False
    try:
        nombre = request.POST["txtNameMat"]
        marca = request.POST.get("txtMarcaMat",None)
        descripcion = request.POST.get("txtDescripcionMat",None)
        estado = request.POST["cbEstadoMat"]        
        deposito = request.POST["cbDepositoMat"]
        estante = request.POST.get("numEstanteMat",False)
        entrepano = request.POST.get("numEntrepanoMat",False)
        locker = request.POST.get("numLockerMat",False)
        with transaction.atomic():
            cantidad = Elemento.objects.all().filter(eleTipo='MAT').count()
            codigoElemento = "MAT" + str(cantidad+1).rjust(6,'0')
            
            elemento = Elemento(eleCodigo = codigoElemento, eleNombre = nombre, eleTipo = "MAT",
                                eleEstado = estado)
            elemento.save()
            
            material = Material(matReferencia = descripcion, matMarca = marca,
                                matElemento = elemento)
            material.save()
            
            ubicacion = UbicacionFisica(ubiDeposito = deposito, ubiEstante = estante,
                                       ubiEntrepano = entrepano, ubiLocker = locker, ubiElemento = elemento)
            ubicacion.save()
            estado = True
            mensaje = f"Material registrado satisfactoriamente con el codigo {codigoElemento}"
            retorno = {"mensaje":mensaje,"estado":estado}
    except Error as error:
        transaction.rollback()
        mensaje = f"Error"
    retorno = {"mensaje":mensaje,"material":material, "estado":estado}
    return render(request, "asistente/registrarMaterial.html",retorno)

def vistaRegistrarProveedor(request):
    Listaproveedor = tipoProveedor
    retorno = {"Listaproveedor":Listaproveedor}
    return render(request, "administrador/registrarProveedor.html", retorno)

def registrarProveedor(request):
    estado = False
    try:
        tipoProveedorFor = request.POST["cbTipoPro"]
        identificacion = request.POST["txtIdentificacion"]
        nombreProveedor = request.POST["txtNombrePro"]
        representante = request.POST.get("txtNombreRepre", None)
        telefono = request.POST.get("numTelefono", None)
        with transaction.atomic():
            proveedor = Proveedor(proTipo = tipoProveedorFor, proIdentificacion = identificacion,
                                  proNombre = nombreProveedor, proRepresentanteLegal = representante,
                                  proTelefono = telefono)
            proveedor.save()
            estado = True
            mensaje = f"Proveedor registrado correctamente"
    except Error as error:
        transaction.rollback()
        mensaje = "Error"
    retorno = {"mensaje": mensaje, "proveedor": proveedor,"estado":estado}
    return render (request, "administrador/registrarProveedor.html", retorno)

def vistaRegistrarUnidad(request):
    return render(request, "administrador/registrarUnidadMedida.html")

def registrarUnidad(request):
    estado = False
    try:
        nombreUni = request.POST["txtUnidad"]
        with transaction.atomic():
            unidad = UnidadMedida(uniNombre = nombreUni)
            unidad.save()
            estado = True
            mensaje = f"Unidad agregada correctamente"
    except Error as error:
        transaction.rollback()
        mensaje = f"Error"
    retorno = {"mensaje":mensaje, "unidad":unidad, "estado":estado}
    return render(request, "administrador/registrarUnidadMedida.html", retorno)
            
def vistaEntradaMaterial(request): 
    proveedores = Proveedor.objects.all()
    usuarios = User.objects.all()
    materiales = Material.objects.all()
    unidadesMed = UnidadMedida.objects.all()
    estados = estadosElementos
    
    retorno = {"listaProveedor":proveedores, "listaUsuario":usuarios, "listaMaterial":materiales, "listaUnidad":unidadesMed, "listaEstado": estados}
    return render(request, "asistente/registrarEntradaMat.html", retorno)

def registrarEntradaMaterial(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():            
                estado = False
                codigoFactura = request.POST['codigoFactura']
                entregadoPor = request.POST['entregadoPor']
                idProveedor = int(request.POST['proveedor'])
                recibidoPor = int(request.POST['recibidoPor'])
                fechahora = request.POST.get('fechaHora',None)
                observaciones = request.POST['observaciones']
                userRecibe = User.objects.get(pk=recibidoPor)
                proveedor = Proveedor.objects.get(pk=idProveedor)
                entradaMaterial = EntradaMaterial (entNumeroFactura = codigoFactura, entFechaHora = fechahora,
                                                    entUsuarioRecibe= userRecibe, entEntregadoPor = entregadoPor,
                                                    entProveedor = proveedor, entObservaciones=observaciones)
                entradaMaterial.save()
                detalleMateriales = json.loads(request.POST['detalle'])
                for detalle in detalleMateriales:
                    material = Material.objects.get(id=int(detalle['idMaterial']))
                    cantidad = int(detalle['cantidad'])
                    precio = int(detalle['precio'])
                    estado = detalle['estado']
                    unidadMedida = UnidadMedida.objects.get(pk=int(detalle['idUnidadMedida']))
                    detalleEntrada = DetalleEntradaMaterial (detEntradaMaterial = entradaMaterial,
                                                        detMaterial = material, detUnidadMedida = unidadMedida,
                                                        detCantidad=cantidad, detPrecioUnitario = precio, devEstado=estado)
                    detalleEntrada.save()
                estado=True
                mensaje="Se ha registrado la entrada de Materiales correctamente"
        except Error as error:
            transaction.rollback()
            mensaje= f"{error}"
        retorno={"estado":estado, "mensaje":mensaje}
        return JsonResponse(retorno)

def listaMateriales(request):
    if request.user.is_authenticated:
        materiales = Material.objects.all()
        retorno = {"listaMateriales":materiales}
        return render (request, "asistente/gestionarMaterial.html",retorno)
    else:
        retorno={"mensaje":"Debe ingresar Sesion"}
        return render(request, "iniciarSesion.html",retorno)
    
def vistaRegistrarSolicitud(request):
    if request.user.is_authenticated:
        elementos = Elemento.objects.all()
        ficha = Ficha.objects.all()
        unidadesMed = UnidadMedida.objects.all()
        retorno = {"listaElemento":elementos, "listaFicha": ficha, "listaUnidad":unidadesMed }
        return render(request, "instructor/registrarSolicitud.html", retorno)
    else:
        mensaje = "Debe Iniciar Sesion"
        return render(request,"iniciarSesion.html",{"mensaje":mensaje})
    
def listaSolicitud(request):
    if request.user.is_authenticated:
        solicitud = SolicitudElemento.objects.all()
        retorno = {"listaSolicitud":solicitud}
        return render (request, "instructor/gestionarSolicitud.html",retorno)
    else:
        retorno={"mensaje":"Debe ingresar Sesion"}
        return render(request, "iniciarSesion.html",retorno)

def registrarSolicitudMaterial(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():            
                estado = False
                ficha = int(request.POST['ficha'])
                nombreProyecto = request.POST['nombreProyecto']
                fechaRequiere = request.POST['fechaRequerida']
                fechaSalida = request.POST['fechaFinal']
                observaciones = request.POST['observaciones']
                fichaaLlevarMaterial = Ficha.objects.get(pk=ficha)
                solicitudMaterial = SolicitudElemento(solProyecto = nombreProyecto, solFicha = fichaaLlevarMaterial,
                                                      solUsuario = request.user,
                                                    solFechaHoraRequerida= fechaRequiere, solEstado = "Solicitada",
                                                    solObservaciones = observaciones)
                solicitudMaterial.save()
                detalleSolicitud = json.loads(request.POST['detalleSolicitud'])
                for detalle in detalleSolicitud:
                    elemento = Elemento.objects.get(id=int(detalle['idSolicitud']))
                    cantidad = int(detalle['cantidad'])
                    unidadMedida = UnidadMedida.objects.get(pk=int(detalle['idUnidadMedida']))
                    detalleSolicitud = DetalleSolicitud(detElemento = elemento,
                                                        detSolicitud = solicitudMaterial, detUnidadMedida = unidadMedida,
                                                        detCantidadRequerida=cantidad)
                    detalleSolicitud.save()
                    usuarios = User.objects.all()
                    
                    for usuario in usuarios:
                        if usuario.groups.filter(name="Administrador").exists():
                            correoAdministrador = usuario.email
                            break
                    asunto = 'Solicitud en nuestro Sistema CIES-NEIVA'
                    mensaje =f'Cordial saludo, <b> {request.user.first_name} {request.user.last_name} </b> \
                    informarle que hemos recibido su solicitud de elementos en nuestro sistema \
                        del centro de la Industria, la Empresa y los Servicios CIES de la ciudad \
                            <br><br><b>Datos de la Solicitud</b> \
                            <br><br><b>Ficha:</b> {fichaaLlevarMaterial.ficCodigo} \
                            <br><b>Programa:</b> {fichaaLlevarMaterial.ficNombre} \
                            <br><b>Proyecto:</b> {nombreProyecto} \
                            <br><b>Fecha Inicial:</b> {fechaRequiere} \
                            <br><b>Fecha Final:</b> {fechaSalida} \
                            <br><br> El administrador procesara su solicitud para su revision y aprobacion \
                            <br> Lo invitamos a ingresar a nuestro sistema para la revision de sus soliitudes en la url:'
                    thread = threading.Thread(target=enviarCorreo,
                                              args=(asunto,mensaje,[request.user.email, correoAdministrador]))
                    thread.start()
                    estado=True
                    mensaje="Se ha registrado la solicitud de Material correctamente"
        except Error as error:
            transaction.rollback()
            mensaje= f"{error}"
        retorno={"estado":estado, "mensaje":mensaje}
        return JsonResponse(retorno)
