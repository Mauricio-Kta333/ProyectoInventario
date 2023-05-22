$(function() {
  $("#Fimagen").on("change", mostrarImagen);
  $("#FimagenDev").on("change", mostrarImagenDevolutivo);
  // $("#txtcodigo").on("change", validarCodigo);
  $("#cbTipoPro").on("change", condicionParaRequired);
  $("#btnAnexarMaterial").on("click", ventanaModal);
  $("#modalAnexarMaterial .btn-close").on("click", cerrar);
});

function ventanaModal(event) {
  event.preventDefault();

  // Validar el formulario antes de mostrar la ventana modal
  if (document.getElementById("frmEntradaMaterial").checkValidity()) {
    // Mostrar la ventana modal
    $("#modalAnexarMaterial").modal("show");
    // Enfocar en el campo "numCantidad" al mostrar el modal
    document.getElementById("numCantidad").focus();
  } else {
    // Enfocar en el primer campo no válido del formulario principal
    var firstInvalidField = document.querySelector("#frmEntradaMaterial :invalid");
    if (firstInvalidField) {
      firstInvalidField.focus();
    }
  }
}

function cerrar() {
  $("#modalAnexarMaterial").modal("hide");
}

function mostrarImagen(evt) {
  const archivos = evt.target.files
  const archivos2 = archivos[0]
  const url = URL.createObjectURL(archivos2)
  let nombre = archivos[0].name
  let tamaño = archivos[0].size
  let extension = nombre.split('.').pop()
  extension = extension.toLowerCase()
  if (extension != "jpg") {
    Swal.fire('Cargar imagen', 'Solo se permiten archivos JPG', 'warning')
    $("#Fimagen").val("")
  } else if (tamaño > "200000") {
    Swal.fire('Cargar imagen ', 'Solo se permiten archivos menores a 50k', 'warning')
    $("#Fimagen").val("")
  } else {
    $("#imagenusuario").attr("src", url)
  }
}

function mostrarImagenDevolutivo(evt) {
  const archivos = evt.target.files
  const archivos2 = archivos[0]
  const url = URL.createObjectURL(archivos2)
  let nombre = archivos[0].name
  let tamaño = archivos[0].size
  let extension = nombre.split('.').pop()
  extension = extension.toLowerCase()
  if (extension != "jpg") {
    Swal.fire('Cargar imagen', 'Solo se permiten archivos JPG', 'warning')
    $("#FimagenDev").val("")
  } else if (tamaño > "200000") {
    Swal.fire('Cargar imagen ', 'Solo se permiten archivos menores a 50k', 'warning')
    $("#FimagenDev").val("")
  } else {
    $("#imagendevo").attr("src", url)
  }
}

// function validarCodigo(evt) {
// location.href="/validarCodigo/" + $("txtcodigo").val()

// }

function abrirModalEliminar(idUsario) {
  Swal.fire({
    title: 'Eliminar Usuario',
    text: "¿Están seguros de eliminar?",
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#3085d6',
    cancelButtonColor: '#d33',
    cancelButtonText: 'No',
    confirmButtonText: 'Si'
  }).then((result) => {
    if (result.isConfirmed) {
      location.href = "/eliminarUsuario/" + idUsario
    }
  })
}

function condicionParaRequired() {
  var cbTipoPro = document.getElementById("cbTipoPro");
  var txtNombreRepre = document.getElementById("txtNombreRepre");

  cbTipoPro.addEventListener("change", function () {
    if (cbTipoPro.value === "Persona Júridica") {
      txtNombreRepre.setAttribute("required", "required");
    } else {
      txtNombreRepre.removeAttribute("required");
    }
  });
}
