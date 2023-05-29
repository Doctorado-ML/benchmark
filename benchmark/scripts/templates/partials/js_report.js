$(document).ready(function () {
    // Check if row is selected
    $('#report-table tbody').on('click', 'tr', function () {
        if ($(this).hasClass('{{ selected }}')) {
            $(this).removeClass('{{ selected }}');
        } else {
            $('#report-table tbody tr.{{ selected }}').removeClass("{{ selected }}")
            $(this).addClass('{{ selected }}');
        }
    });
    $(document).ajaxStart(function(){ 
        $("body").addClass('ajaxLoading');
    });
    $(document).ajaxStop(function(){ 
        $("body").removeClass('ajaxLoading');
    });
  });
  function excelFile() {
    var selectedFiles = ["{{ file }}"];
    // send data to server with ajax post
    $.ajax({
        type:'POST',
        url:'/excel',
        data: JSON.stringify(selectedFiles),
        contentType: "application/json",
        dataType: 'json',
        success: function(data){
            alert("Se ha generado el archivo "+data.file);
        },
        error: function (xhr, ajaxOptions, thrownError) {
            var mensaje = JSON.parse(xhr.responseText || '{\"mensaje\": \"Error indeterminado\"}');
            alert(mensaje.mensaje);
        }
    });
}