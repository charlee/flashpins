
# Add/Edit Pin Dialog

$ = jQuery

##
# base dialog
#
$.widget 'idv2.baseDialog',

  
  _create: ->
  
    # dialog frame
    @dialog = $("<div>").addClass("modal hide fade").appendTo(@element)

    # dialog header
    @header = $("<div>").addClass("modal-header").appendTo(@dialog)
    $("<button>").addClass("close").html("&times;").appendTo(@header).click =>
      @close()
    @title = $("<h3>").appendTo(@header)

    # dialog body
    @body = $("<div>").addClass("modal-body").appendTo(@dialog)
    @error = $("<div>").addClass("alert alert-error").hide().appendTo(@body)

    # dialog footer
    @footer = $("<div>").addClass("modal-footer").appendTo(@dialog)


  ##
  # hide error msg
  #
  hideError: ->
    @error.hide()

  ##
  # show error msg
  #
  showError: (msg)->
    @error.slideDown().html(msg)

  
  ##
  # close dialog
  #
  close: ->
    @dialog.modal('hide')
    @clear()

  ##
  # open dialog
  #
  open: ->
    @dialog.modal('show')

  ##
  # clear contents
  #
  clear: ->
    @hideError()


##
# user base dialog
#
$.widget 'idv2.userBaseDialog', $.idv2.baseDialog,

  _create: ->
    @_super()

    # dialog frame
    @dialog.addClass('user-dialog')

    # body elements
    @email = $("<input type='text'>").addClass('text').attr("placeholder", "E-mail").appendTo(@body)
    @password = $("<input type='password'>").addClass('text').attr("placeholder", "Password").appendTo(@body)

  clear: ->
    @_super()
    @email.val('')
    @password.val('')



##
# pin dialog
#
$.widget 'idv2.pinDialog', $.idv2.baseDialog,

  _create: ->

    @_super()

    # dialog frame
    @dialog.addClass("pin-dialog")

    # dialog body elements
    @pinTitle = $("<input type='text'>").addClass('text').attr("placeholder", "Title").appendTo(@body)
    @pinURL = $("<input type='text'>").addClass('text').attr("placeholder", "URL").appendTo(@body);
    @pinDesc = $("<textarea>").addClass('text').attr("placeholder", "Description").appendTo(@body);
    @pinTags = $("<input type='text'>").attr("placeholder", "Tags").appendTo(@body).tagtag();

    # dialog footer
    $("<button>").addClass("btn").html("Cancel").appendTo(@footer).click =>
      @close()
    $("<button>").addClass("btn btn-primary").html("Save").appendTo(@footer).click =>
      @save()

   
  ##
  # open dialog
  # - ac
  # - action: 'new' or 'edit' or 'pin'
  # - data: data used for pin edit when action == 'edit'
  #
  open: (action, data) ->
    
    @action = action

    switch action
      when 'new'
        @title.html("Add Pin")
        @clear()

      when 'pin'
        @title.html("Add Pin")
        $.get('/j/links/' + parseInt(data.id), (data) =>
          @pinTitle.val(data.title)
          @pinURL.val(data.url)
          @pinTags.val(data.tags.join(','))
          @pinTags.tagtag("importTags")
        , 'json')
          
      when 'edit'
        @title.html("Edit Pin")
        @pinId = data.id
        $.get('/j/pins/' + parseInt(data.id), (data) =>
          @pinTitle.val(data.title)
          @pinDesc.val(data.desc)
          @pinURL.val(data.link.url)
          @pinTags.val(data.tags.join(','))
          @pinTags.tagtag("importTags")
        , 'json')

    @_super()


  ##
  # clear contents
  #
  clear: ->
    @_super()
    @pinTitle.val('')
    @pinURL.val('')
    @pinDesc.val('')
    @pinTags.val('')

  ##
  # Save content to server and close dialog
  #
  save: ->

    pin = 
      title: @pinTitle.val()
      url: @pinURL.val()
      desc: @pinDesc.val()
      tags: @pinTags.val()

    errorHandler = ->
    
    successHandler = =>
      @close()
      location.reload()

    # TODO: data validation
    switch @action

      when 'new', 'pin'
        # TODO: data validation
        $.ajax '/j/pins/'
          type: 'POST',
          contentType: 'application/json'
          data: JSON.stringify(pin)
          success: successHandler
          error: errorHandler

      when 'edit'
        $.ajax '/j/pins/' + parseInt(@pinId),
          type: 'PATCH'
          contentType: 'application/json'
          data: JSON.stringify(pin)
          success: successHandler
          error: errorHandler

      

##
# pin dialog
#
$.widget 'idv2.pinDeleteDialog', $.idv2.baseDialog,

  _create: ->

    @_super()

    # dialog frame
    @dialog.addClass("pin-dialog")

    @title.html("Delete Pin")

    # dialog body elements
    $("<div>").html("Are you sure to delete this pin?").appendTo(@body)

    # dialog footer
    $("<button>").addClass("btn").html("Cancel").appendTo(@footer).click =>
      @close()

    $("<button>").addClass("btn btn-danger").html("Delete").appendTo(@footer).click =>
      @remove()

  ##
  # open dialog
  #
  open: (data) ->

    @pinId = data.id

    @_super()


  ##
  # delete pin
  #
  remove: ->
    
    $.ajax '/j/pins/' + parseInt(@pinId),
      type: 'DELETE'
      contentType: 'application/json'
      success: =>
        @close()
        location.reload()







