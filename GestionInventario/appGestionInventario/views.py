from django.shortcuts import render, redirect
from django.db import Error, transaction
from django.contrib.auth.models import *
from appGestionInventario.models import *
import random
import string, os


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
            #enviar correo al ususario
            return redirect("/vistagestionarUsuario/",retorno)
    except Error as error:
        transaction.rollBack()
        mensaje = f"{error}"
    retorno = {"mensaje": mensaje, "user": user}
    return render(request, "administrador/registrarUsuario.html", retorno)

def vistaRegistrarUsuario(request):
    roles = Group.objects.all()
    tipos = tipoUsuario
    retorno = {"roles":roles,"user":None, "tipoUsuario":tipos}
    return render(request, "administrador/registrarUsuario.html", retorno)

def listaUsuarios(request):
    try:
        usuario = User.objects.all()
        mensaje = ""
    except Error as error:
        mensaje = f"Problemas al listar los usuarios {error}"
    
    retorno = {"mensaje": mensaje, "listaUsuarios":usuario}
    return render(request, "administrador/gestionarUsuarios.html", retorno)

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

def actualizarProducto(request):
    idUsuario = int(request.POST["id"])
    nombre = request.POST["txtNombre"]
    apellido = request.POST["txtApellido"]
    correo = request.POST["txtCorreo"]
    tipo = request.POST["cbTipo"]
    foto = request.FILES.get("Fimagen", False)
    idRol = int(request.POST["cbRol"])
    try:
        rol = Group.objects.get(id=idRol)
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