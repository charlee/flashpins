$(document).ready ->

  # init the pin dialog
  $("#pin-dialog").pinDialog()
  $("#pin-delete-dialog").pinDeleteDialog()

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

  # delete a pin
  $("a.pin-delete").click ->
    $("#pin-delete-dialog").pinDeleteDialog("open", { id: parseInt($(@).attr("pin_id")) })
    false

  # replace pin url with short url
  $(".pin a.pin_url").each ->
    e = $(@)
    e.click ->
      e.attr("href", "/i/" + e.attr("link_id"))
      true

