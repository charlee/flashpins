/**
 * Add/Edit Pin Dialog
 */

(function($) {


  /**
   * base dialog
   */
  $.widget('idv2.baseDialog', {

    _create: function() {

      var root = this;

      // dialog frame
      this.dialog = $("<div>").addClass("modal hide fade").appendTo(this.element);

      // dialog header
      this.header = $("<div>").addClass("modal-header").appendTo(this.dialog);
      $("<button>").addClass("close").html("&times;").click(function() {
        root.close();
      }).appendTo(this.header);
      this.title = $("<h3>").appendTo(this.header);

      // dialog body
      this.body = $("<div>").addClass("modal-body").appendTo(this.dialog);

      this.error = $("<div>").addClass('alert alert-error').hide().appendTo(this.body);

      // dialog footer
      this.footer = $("<div>").addClass("modal-footer").appendTo(this.dialog);

    },

    /**
     * hide error msg
     */
    hideError: function() {
      this.error.hide();
    },

    /**
     * show error msg
     */
    showError: function(msg) {
      this.error.slideDown().html(msg);
    },


    /**
     * Close dialog
     */
    close: function() {
      this.dialog.modal('hide');
      this.clear();
    },

    /**
     * Open dialog
     */
    open: function() {
      this.dialog.modal('show');
    },

    clear: function() {
      this.hideError();
    },


  });

  /**
   * user base dialog
   */
  $.widget('idv2.userBaseDialog', $.idv2.baseDialog, {


    /**
     * Create the dialog elements
     */
    _create: function() {

      this._super();

      // dialog frame
      this.dialog.addClass('user-dialog');

      // body elements
      this.email = $("<input type='text'>").addClass('text').attr("placeholder", "E-mail").appendTo(this.body);
      this.password = $("<input type='password'>").addClass('text').attr("placeholder", "Password").appendTo(this.body);
    },


    clear: function() {
      this._super();
      this.email.val('');
      this.password.val('');
    },

  });


  /**
   * login dialog
   */
  $.widget('idv2.loginDialog', $.idv2.userBaseDialog, {

    _create: function() {

      var root = this;

      this._super();
      this.title.html('Login');

      this.loginBtn = $("<button>").addClass("btn btn-primary").html("Login").click(function() {
        root.login();
      }).appendTo(this.footer);
    },

    login: function() {
      var user = {
        email: this.email.val(),
        password: this.password.val()
      },

      root = this;

      if (user.email === '') {
        this.showError("Please enter your E-mail address.");
      } else if (user.password === '') {
        this.showError("Please enter your password.");
      } else {

        this.hideError();
        $.post('/j/login', user, function(data) {

          if (data.result == 'success') {
            location.href = '/';
          } else {
            // show error
            root.showError(data.errmsg);
          }

        }).fail(function() {
        });
      }
    },

  });


  /**
   * sign up dialog
   */
  $.widget('idv2.signupDialog', $.idv2.userBaseDialog, {

    _create: function() {

      var root = this;

      this._super();
      this.title.html('Sign Up');

      this.passwordConfirm = $("<input type='password'>").addClass('text').attr("placeholder", "Confirm Password").appendTo(this.body);

      this.signupBtn = $("<button>").addClass("btn btn-primary").html("Sign Up").click(function() {
        root.signup();
      }).appendTo(this.footer);
    },

    clear: function() {
      this._super();
      this.passwordConfirm.val('');
    },

    signup: function() {

      var user = {
        email: this.email.val(),
        password: this.password.val(),
        passwordConfirm: this.passwordConfirm.val()
      },

      root = this;

      // TODO: validation

      $.post('/j/signup', user, function(data) {

        if (data.result == 'success') {
          location.href = '/';
        } else {
          // TODO: show error
        }

      }).fail(function() {
      });
    },

  });


  $.widget("idv2.pinDialog", $.idv2.baseDialog, {

    /**
     * Create the dialog elements
     */
    _create: function() {

      var root = this;

      this._super();

      // dialog frame
      this.dialog.addClass("pin-dialog");

      // dialog body elements
      this.pinTitle = $("<input type='text'>").addClass('text').attr("placeholder", "Title").appendTo(this.body);
      this.pinURL = $("<input type='text'>").addClass('text').attr("placeholder", "URL").appendTo(this.body);
      this.pinDesc = $("<textarea>").addClass('text').attr("placeholder", "Description").appendTo(this.body);
      this.pinTags = $("<input type='text'>").attr("placeholder", "Tags").appendTo(this.body).tagtag();

      // dialog footer
      $("<button>").addClass("btn").html("Cancel").click(function() {
        root.close();
      }).appendTo(this.footer);
      $("<button>").addClass("btn btn-primary").html("Save").click(function() {
        root.save();
      }).appendTo(this.footer);
    },


    /**
     * Open dialog
     * - action: 'new' or 'edit' or 'pin'
     * - data: data used for pin edit when action == 'edit'
     */
    open: function(action, data) {

      var root = this;
      this.action = action;

      if (action == 'new') {

        this.title.html("Add Pin");
        this.clear();

      } else if (action == 'pin') {

        this.title.html("Add Pin");

        // TODO: add loading mask
        $.get('/j/links/' + parseInt(data.id), function(data) {

          root.pinTitle.val(data.title);
          root.pinURL.val(data.url);
          root.pinTags.val(data.tags.join(','));
          root.pinTags.tagtag("importTags");        // refresh loaded tags

          // TODO: remove loading mask
        }, 'json');

      } else if (action == "edit") {
        this.title.html("Edit Pin");

        // TODO: add loading mask
        this.pinId = data.id;

        $.get('/j/pins/' + parseInt(data.id), function(data) {

          root.pinTitle.val(data.title);
          root.pinURL.val(data.url);
          root.pinDesc.val(data.desc);
          root.pinTags.val(data.tags.join(','));
          root.pinTags.tagtag("importTags");        // refresh loaded tags
          
          // TODO: remove loading mask
        }, 'json');

      }

      this._super();

    },


    /**
     *
     */
    clear: function() {
      this._super();
      this.pinTitle.val('');
      this.pinURL.val('');
      this.pinDesc.val('');
      this.pinTags.val('');
    },


    /**
     * Save content to server and close dialog
     */
    save: function() {
      
      var pin = {
        title: this.pinTitle.val(),
        url: this.pinURL.val(),
        desc: this.pinDesc.val(),
        tags: this.pinTags.val()
      },

      root = this,

      errorHandler = function() {
      },

      successHandler = function() {
        root.close();
        location.reload();
      };

      // TODO: data validation
      if (this.action == 'new' || this.action == 'pin') {

        // TODO: data validation

        $.post('/j/pins', pin, successHandler).fail(errorHandler);

      } else if (this.action == 'edit') {

        $.post('/j/pins/' + parseInt(this.pinId), pin, successHandler).fail(errorHandler);
      }
    },

  });

})(jQuery);


