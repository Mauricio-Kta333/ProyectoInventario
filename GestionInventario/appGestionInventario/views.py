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
        foto = request.FILES.get("Fimagen", False)
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
                                    args=(asunto,mensaje,user.email))
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
    return render(request, "administrador/editar.html", retorno)

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
    return render (request, "administrador/editar.html", retorno)

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
    if request.user.is_authenticated:
        return render(request, "administrador/inicio.html")
    else:
        mensaje = "Debe iniciar sesion"
        retorno = {"mensaje":mensaje}
        return render(request,'iniciarSesion.html', retorno) 

def inicioAsistente(request):
    if request.user.is_authenticated:
        return render(request, "asistente/inicio.html")
    
def inicioInstructor(request):
    if request.user.is_authenticated:
        return render(request, "instructor/inicio.html")
    
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
        correo = EmailMultiAlternatives(asunto,mensaje,remitente,[destinatario])
        correo.attach_alternative(contenido, 'text/html')
        correo.send(fail_silently=True)
    except SMTPException as error:
        print(error)

def vistagestionarDevolutivo(request):
    if request.user.is_authenticated:
        elementosDevolutivos = Devolutivo.objects.all()
        retorno = {"listaElementosDevolutivos": elementosDevolutivos}
        return render(request,"administrador/gestionarDevolutivo.html", retorno)
    else:
        mensaje = "Debe Iniciar Sesion"
        return render(request,"iniciarSesion.html",{"mensaje":mensaje})
    
def vistaRegistrarDevolutivo(request):
    if request.user.is_authenticated:
        retorno = {"tipoElemento":tipoElemento, "estados": estadosElementos, "depositos":ubicacionDeposito }
        return render(request, "administrador/registrarDevolutivo.html", retorno)
    else:
        mensaje = "Debe Iniciar Sesion"
        return render(request,"iniciarSesion.html",{"mensaje":mensaje})

def registrarDevolutivo(request):
    estado = False
    try:
        placaSena = request.POST["txtPlacaSena"]
        fechaInventario = request.POST["txtFechaSena"]
        tipoElemento = request.POST["cbTipoEle"]
        serial = request.POST.get("txtSerial", False)
        marca = request.POST.get("txtMarca", False)
        valorUnitario = int(request.POST["txtValor"])
        estado = request.POST["cbEstado"]
        nombre = request.POST["txtNombre"]
        descripcion = request.POST["txtDescripcion"]
        deposito = request.POST["cbDeposito"]
        estante = request.POST.get("numEstante",False)
        entrePano = request.POST.get("numEntrepano", False)
        locker = request.POST.get("numLocker",False)
        archivo = request.FILES.get("FimagenDev", False)
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
    return render (request,"administrador/registrarDevolutivo.html",retorno)

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
    return render(request, "administrador/editarAdmin.html", retorno)

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
    return render (request, "administrador/editarAdmin.html", retorno)

def cerrarSesion(request):
    logout(request)
    return redirect('/inicioSesion/')
