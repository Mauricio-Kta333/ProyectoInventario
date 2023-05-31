let elementos =[]
let solicitudMateriales=[]
let unidadesMedidas=[]
$(function(){
    //se utiliza para las peticiones ajax con query
    $.ajaxSetup({
        headers:{
            'X-CSRFToken':getCookie('csrftoken')
        }
    })

    $("#btnAgregarMaterialSolicitud").click(function(){
        agregarMaterialSolicitud();
    })

    $("#btnRegistrarSolicitud").click(function(){
        registroSolicitudMaterial();
    })
})

function getCookie(name){
    let cookieValue = null;
    if (document.cookie && document.cookie !== ''){
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0,name.length + 1) === (name + '=')){
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
            
        }
    }
    return cookieValue;
}

function registroSolicitudMaterial(){
    var datos = {
        "ficha": $("#cbFicha").val(),
        "nombreProyecto": $("#txtNombreProyecto").val(),
        "fechaRequerida": $("#datFechaRequiere").val(),
        "fechaFinal": $("#datFechaFinal").val(),
        "observaciones": $("#txtObservacionS").val(),
        "detalleElemento": JSON.stringify(solicitudMateriales),
    }
    $.ajax({
        url: "/registrarEntradaMaterial/",
        data: datos,
        type: 'post',
        dataType: 'json',
        cache: false,
        success: function(resultado){
            console.log(resultado);
            if(resultado.estado){
                frmMaterialSolicitado.reset();
                solicitudMateriales.length=0;
                mostrarDatosTabla();
            }
            Swal.fire("Registro de Solicitud Material",resultado.mensaje,"success")
        }
    })
}

function agregarMaterialSolicitud(){
    //averigua si ya se ha ingresado el material
    const m = solicitudMateriales.find(solicitud=>solicitud.idSolicitud == $('#cbElemento').val());
    if(m==null){
        const solicitud = {
        "idSolicitud": $("#cbElemento").val(),
        "cantidad": $("#numCantidadE").val(),
        "idUnidadMedida": $("#cbUnidadMedE").val(),       
        }
        solicitudMateriales.push(solicitud);
        mostrarDatosTablaSolicitud()
        document.getElementById("frmModalSolicitud").reset();
    }else{
        Swal.fire("Registro de Solicitud Material","El material ingresado ya ha agregado en el Detalle. Verifique","info")
    }
}

function mostrarDatosTablaSolicitud(){
    datos = "";
    solicitudMateriales.forEach(solicitudTa =>{
        posE = elementos.findIndex(elemento=>elemento.idSolicitud==solicitudTa.idSolicitud);
        posU = unidadesMedidas.findIndex(unidad=>unidad.id == solicitudTa.idUnidadMedida);

        datos+= "<tr class='text-center'>"
        datos+= "<td class'text-center'>"+ elementos[posE].codigo +"</td>"
        datos+= "<td>"+ elementos[posE].nombre +"</td>"
        datos+= "<td class'text-center'>"+ solicitudTa.cantidad +"</td>"
        datos+= "<td>"+ unidadesMedidas[posU].nombre +"</td>"
        datos+= "</tr>"
    });
    document.getElementById("datosTablasSolicitudes").innerHTML = datos;
}

function cargarMaterialSolicitud(idSolicitud,codigo,nombre){
    const solicitud = {
        "idSolicitud" : idSolicitud,
        "codigo" : codigo,
        "nombre" : nombre
    }
    elementos.push(solicitud);
}

function cargarUnidadesMedida(id,nombre){
    const unidadMedida = {
        "id" : id,
        "nombre" : nombre
    }
    unidadesMedidas.push(unidadMedida);
}