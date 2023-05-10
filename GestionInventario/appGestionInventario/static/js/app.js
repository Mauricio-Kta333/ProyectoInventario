$(function () {
    $("#Fimagen").on("change", mostrarImagen);
    // $("#txtcodigo").on("change", validarCodigo);
})

function mostrarImagen(evt) {
    const archivos = evt.target.files
    const archivos2 = archivos[0]
    const url = URL.createObjectURL(archivos2)
    let nombre = archivos[0].name
    let tamaño = archivos[0].size
    let extension = nombre.split('.').pop()
    extension = extension.toLowerCase()
    if (extension != "jpg") {
        Swal.fire('Cargar imagen Producto', 'Solo se permiten archivos JPG', 'warning')
        $("#Fimagen").val("")
    } else if (tamaño > "200000") {
        Swal.fire('Cargar imagen Producto', 'Solo se permiten archivos menores a 50k', 'warning')
        $("#Fimagen").val("")
    } else {
        $("#imagenproducto").attr("src", url)
    }
       
}

// function validarCodigo(evt) {
// location.href="/validarCodigo/" + $("txtcodigo").val()

// }

function abrirModalEliminar(idUsario) {
    Swal.fire({
      title: 'Eliminar Usuario',
      text: "¿Estan seguros de eliminar?",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      cancelButtonText: 'No',
      confirmButtonText: 'Si'
    }).then((result) => {
      if (result.isConfirmed) {
        location.href ="/eliminarUsuario/"+idUsario
      }
    })
  }
