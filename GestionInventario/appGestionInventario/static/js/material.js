let materiales =[]
let entradaMateriales=[]
let unidadesMedidas=[]
$(function(){
    //se utiliza para las peticiones ajax con query
    $.ajaxSetup({
        headers:{
            'X-CSRFToken':getCookie('csrftoken')
        }
    })

    $("#btnAgregarMaterialDetalle").click(function(){
        agregarMaterialDetalle();
    })
    $("#entradaMaterial").click(function(){
        vistaEntradaMaterial();
    })
    $("#btnRegistrarDetalle").click(function(){
        registroDetalleEntrada();
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

function registroDetalleEntrada(){
    var datos = {
        "codigoFactura": $("#txtCodigoFac").val(),
        "entregadoPor": $("#txtEntrega").val(),
        "proveedor": $("#cbProveedor").val(),
        "recibidoPor": $("#cbRecibidoPor").val(),
        "observaciones": $("#txtObservacion").val(),
        "fechaHora": $("#datFechaEntre").val(),
        "detalle": JSON.stringify(entradaMateriales),
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
                frmEntradaMaterial.reset();
                entradaMateriales.length=0;
                mostrarDatosTabla();
            }
            Swal.fire("Registro de Materiales",resultado.mensaje,"success")
        }
    })
}

function agregarMaterialDetalle(){
    //averigua si ya se ha ingresado el material
    const m = entradaMateriales.find(material=>material.idMaterial == $('#cbMaterial').val());
    if(m==null){
        const material = {
        "idMaterial": $("#cbMaterial").val(),
        "cantidad": $("#numCantidad").val(),
        "precio": $("#numPrecio").val(),
        "idUnidadMedida": $("#cbUnidadMed").val(),
        "estado": $("#cbEstadoEntra").val(),        
        }
        entradaMateriales.push(material);
        mostrarDatosTabla()
        document.getElementById("frmModal").reset();
    }else{
        Swal.fire("Registro de Materiales","El material ingresado ya ha agregado en el Detalle. Verifique","info")
    }
}

function mostrarDatosTabla(){
    datos = "";
    entradaMateriales.forEach(entrada =>{
        posM = materiales.findIndex(material=>material.idMaterial==entrada.idMaterial);
        posU = unidadesMedidas.findIndex(unidad=>unidad.id == entrada.idUnidadMedida);

        datos+= "<tr>"
        datos+= "<td class'text-center'>"+ materiales[posM].codigo +"</td>"
        datos+= "<td>"+ materiales[posM].nombre +"</td>"
        datos+= "<td class'text-center'>"+ entrada.cantidad +"</td>"
        datos+= "<td class'text-end'>"+ entrada.precio +"</td>"
        datos+= "<td>"+ unidadesMedidas[posU].nombre +"</td>"
        datos+= "<td class'text-center'>"+ entrada.estado +"</td>"
        datos+= "</tr>"
    });
    document.getElementById("datosTablasMateriales").innerHTML = datos;
}

function cargarMateriales(idMaterial,codigo,nombre){
    const material = {
        "idMaterial" : idMaterial,
        "codigo" : codigo,
        "nombre" : nombre
    }
    materiales.push(material);
}

function cargarUnidadesMedida(id,nombre){
    const unidadMedida = {
        "id" : id,
        "nombre" : nombre
    }
    unidadesMedidas.push(unidadMedida);
}