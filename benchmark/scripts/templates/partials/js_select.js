$(document).ready(function () {
    var table = $('#file-table').DataTable({
        "paging": true,
        "searching": true,
        "ordering": true,
        "info": true,
        "select.items": "row",
        "pageLength": 25,
        "columnDefs": [{
            "targets": 8,
            "orderable": false
        }],
        //"language": {
        //    "lengthMenu": "_MENU_"
        //}
    });
    // Check if row is selected
    $('#file-table tbody').on('click', 'tr', function () {
        if ($(this).hasClass('{{ selected }}')) {
            $(this).removeClass('{{ selected }}');
        } else {
            table.$('tr.{{ selected }}').removeClass('{{ selected }}');
            $(this).addClass('{{ selected }}');
        }
    });
});
function showFile(selectedFile) {
    var form = $('<form action="/show" method="post">' +
        '<input type="hidden" name="selected-file" value="' + selectedFile + '" />' +
        '</form>');
    $('body').append(form);
    form.submit();
}
function excel() {
    var checkbox = document.getElementsByName("selected_files");
    var selectedFiles = [];
    for (var i = 0; i < checkbox.length; i++) {
        if (checkbox[i].checked) {
            selectedFiles.push(checkbox[i].value);
        }
    }
    if (selectedFiles.length == 0) {
        alert("Select at least one file");
        return;
    } 
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
function setCheckBoxes(value) {
    var checkbox = document.getElementsByName("selected_files");
    for (i = 0; i < checkbox.length; i++) {
        checkbox[i].checked=value;
    }
}