$(document).ready(function () {
  var table = $("#file-table").DataTable({
    paging: true,
    searching: true,
    ordering: true,
    info: true,
    "select.items": "row",
    pageLength: 25,
    columnDefs: [
      {
        targets: 8,
        orderable: false,
      },
    ],
    //"language": {
    //    "lengthMenu": "_MENU_"
    //}
  });
  // Check if row is selected
  $("#file-table tbody").on("click", "tr", function () {
    if ($(this).hasClass("{{ select.selected() }}")) {
      $(this).removeClass("{{ select.selected() }}");
    } else {
      table
        .$("tr.{{ select.selected() }}")
        .removeClass("{{ select.selected() }}");
      $(this).addClass("{{ select.selected() }}");
    }
  });
  // Show file with doubleclick
  $("#file-table tbody").on("dblclick", "tr", function () {
    showFile($(this).attr("id"));
  });
  $(document).ajaxStart(function () {
    $("body").addClass("ajaxLoading");
  });
  $(document).ajaxStop(function () {
    $("body").removeClass("ajaxLoading");
  });
  $('#compare').change(function() {
    if ($(this).is(':checked')) {
      $("[name='best_buttons']").removeAttr("hidden");
      $("[name='best_buttons']").addClass("tag is-link is-normal");
    } else {
      $("[name='best_buttons']").attr("hidden", true);
      $("[name='best_buttons']").removeClass("tag is-link is-normal");
    }
  });
  if ($('#compare').is(':checked')) {
      $("[name='best_buttons']").removeAttr("hidden");
      $("[name='best_buttons']").addClass("tag is-link is-normal");
    } else {
      $("[name='best_buttons']").attr("hidden", true);
      $("[name='best_buttons']").removeClass("tag is-link is-normal");
    }
});
function showFile(selectedFile) {
  var form = $(
    '<form action="/show" method="post">' +
      '<input type="hidden" name="selected-file" value="' +
      selectedFile +
      '" />' +
      '<input type="hidden" name="compare" value=' +
      $("#compare").is(":checked") +
      " />" +
      "</form>"
  );
  $("body").append(form);
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
  var compare = $("#compare").is(":checked");
  excelFiles(selectedFiles, compare);
}
function setCheckBoxes(value) {
  var checkbox = document.getElementsByName("selected_files");
  for (i = 0; i < checkbox.length; i++) {
    checkbox[i].checked = value;
  }
}
function redirectDouble(route, parameter) {
  location.href = "/"+ route + "/" + parameter + "/" + $("#compare").is(":checked");
}
function redirectSimple(route) {
  location.href = "/" + route + "/" + $("#compare").is(":checked");
}
