$(document).ready ->

  # init the pin dialog
  $("#pin-dialog").pinDialog()

  # Pin-add button
  $("#btn-pin").click ->
    $("#pin-dialog").pinDialog("open", "new")

  # pin edit link
  $("a.pin-edit").click ->
    $("#pin-dialog").pinDialog("open", "edit", { id: parseInt($(@).attr("pin_id")) })
    false

  # save an existing link to pin
  $("a.pin-save").click ->
    $("#pin-dialog").pinDialog("open", "pin", { id: parseInt($(@).attr("link_id")) })
    false
