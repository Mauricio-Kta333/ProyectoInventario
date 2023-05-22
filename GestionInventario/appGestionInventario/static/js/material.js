let materiales = []
let entradaMateriales = []
let unidadesMedida = []

$(function(){
    $.ajaxSetup({
        headers:{
            'X-CSRFToken':getCookie('csrftoken')
        }
    })
    $("#btnAgregarMaterialDetalle").click(function(){
        agregarDetalleMaterial();
    })
    $("#entradaMaterial").click(function(){
        vistaEntradaMaterial();
    })
    $("#btnRegistrarDetalle").click(function(){
        registroDetalleEntrada();
    })
})

function getCookie(name) {
    let cookieValue = null;
    if(document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
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
        "observaciones" :$("#txtObservacion").val(),
        "fechahora" :$("#datFechaEntre").val(),
        "detalle": JSON.stringify(entradaMateriales),
    };
    $.ajax({
        url: "/registrarEntradaMaterial/",
        data: datos,
        type: "post",
        dataType: 'json',
        cache:false,
        success: function(resultado){
            console.log(resultado) ;
            if(resultado.estado){
                frmDatosGenerales.reset();
                entradaMateriales.length=0;
                mostrarDatosTabla();
            }
        Swal.fire("Registro de Materiales", resultado.mensaje, "success")
        }
    })
}

function agregarDetalleMaterial() {
    const m = entradaMateriales.find(material=>material.idMaterial == $("#cbMaterial").val());
    if(m==null){
        const material = {
            "idMaterial": $("#cbMaterial").val(),
            "cantidad": $("#numCantidad").val(),
            "precio": $("#numPrecio").val(),
            "idUnidadMedida": $("#cbUnidadMed").val(),
            "estado": $("#cbEstadoEntra").val(),
            "observaciones": $("#txtObservacion").val(),
        }
        entradaMateriales.push(material);
        frmEntradaMaterial.reset();
        mostrarDatosTabla();
    }else{
        Swal.fire("Entrada Materiales", "El material seleccionado ya se ha agregado en el Detalle, Verifique", "info");
    }
}

function mostrarDatosTabla(){
    datos = "";
    entradaMateriales.forEach(entrada => {
        posM = materiales.findIndex(material=>material.idMaterial == entrada.idMaterial);
        posU = unidadesMedida.findIndex(unidad=>unidad.id == entrada.idUnidadMedida);
        datos +="<tr>";
        datos += "<td class='text-center'>" + materiales[posM].codigo + "</td>";
        datos += "<td>" + materiales[posM].nombre + "</td>";
        datos += "<td class='text-center'>" + entrada.cantidad + "</td>";
        datos += "<td class='text-end'>" + "$ "+ entrada.precio +".00" + "</td>";
        datos += "<td>" + unidadesMedida[posU].nombre + "</td>";
        datos += "<td class='text-center'>" + entrada.estado + "</td>";
        datos += "</tr>";
    });

    datosTablaMateriales.innerHTML = datos;
}


function cargarMateriales(idMaterial, codigo, nombre) {
    const material = {
        "idMaterial": idMaterial,
        "codigo": codigo,
        "nombre": nombre,
    }
    materiales.push(material);
}

function cargarUnidadesMedida(id, nombre) {
    const unidadMedida = {
        "id": id,
        "nombre": nombre,
    }
    unidadesMedida.push(unidadMedida);
}
