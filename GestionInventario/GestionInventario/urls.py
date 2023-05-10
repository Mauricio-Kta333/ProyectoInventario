"""
URL configuration for GestionInventario project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from appGestionInventario import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path("login/", views.vistaLogin),
    path("inicioSesion/", views.login),
    path('admin/', admin.site.urls),
    path('vistaRegistrarUsuario/',views.vistaRegistrarUsuario),
    path("inicioAdministrador/", views.inicioAdministrador),
    path("inicioAsistente/", views.inicioAsistente),
    path("inicioInstructor/", views.inicioInstructor),
    path('registrarUsuario/', views.registrarUsuario),
    path('vistagestionarUsuario/', views.listaUsuarios),
    path('consultarUsuario/<int:id>/', views.consultarUsuario),
    path('actualizarUsuario/', views.actualizarUsuario),
    path('eliminarUsuario/<int:id>/',views.eliminarUsuario),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)

