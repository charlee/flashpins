/**
 * Copyright (C) 2013 charlee
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a copy of
 * this software and associated documentation files (the "Software"), to deal in
 * the Software without restriction, including without limitation the rights to
 * use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
 * of the Software, and to permit persons to whom the Software is furnished to do
 * so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 */

/**
 *
 * TagTag version 0.1 by charlee
 *
 * Usage:
 *
 * $("#tags").tagtag({      // use .tagtag() on an <input> element
 *  width: 400,             // width of the tag input area
 *  height: 100,            // height of the tag input area
 *  delimiter: ', ',        // delimiters, every chars in the string will be used as a delimiters
 *                          // and the first char will be used as the connector when put data
 *                          // back into original <input>.
 *  onAddTag: callback,     // called after user added a tag.
 *                          // callback(originalInputElement, tagElement, tagContent)
 *  validator: callback     // called to verify if a tag is valid.
 *                          // callback(tagContent)
 * });
 */

(function($) {

  $.widget("idv2.tagtag", {
  
    options: {
      delimiter: ', ',
      onAddTag: null,
      validator: null
    },


    /**
     * initialize
     */
    _create: function() {

      var root = this,
      opt = this.options;

      this.delimiters = opt.delimiter.split('');
      this.element.hide();

      this.container = $("<div>").addClass("tagtag-container")
                                 .attr("role", "textbox")
                                 .insertAfter(this.element);

      this.input = $("<input>").addClass("tagtag-input")
                               .attr("type", "text")
                               .keypress(function(e) { root._onKeyPress(e); })
                               .keydown(function(e) { root._onKeyDown(e); })
                               .focus(function(e) { root._onFocus(e); })
                               .blur(function(e) { root._onBlur(e); })
                               .appendTo(this.container);

      this.container.click(function() { root.input.focus(); });

      this.container.on("click", ".tagtag-tag .tagtag-tagclose", function(e) {
        root._onCloseClick(e);
      });

      if ($.trim(this.element.val()).length > 0) {
        this.importTags();
      }

    },

    /**
     * import tags from original input
     */
    importTags: function() {
      var root = this,
      delimiter = eval("/[" + this.options.delimiter + "]/"),
      ss = $.grep(this.element.val().split(delimiter), function(e) { return !!e; });

      this.clearTags();

      $.each(ss, function(idx, s) {
        root._insertTag(s);

        // remove invalid tags
        root.container.find(".tagtag-taginvalid").remove();
      });
    },


    /**
     * clear tags
     */
    clearTags: function() {
        this.container.find(".tagtag-tag").remove();
        this._updateData();
    },


    /**
     * update tag data into original input
     */
    _updateData: function() {

      var v = this.container.find(".tagtag-tagvalid>.tagtag-tagcontent").map(function(idx, elem) {
        return $(elem).text();
      }).get().join(this.options.delimiter.charAt(0));

      this.element.val(v);
    },
  
    /**
     * make new tag
     */
    _insertTag: function(s) {

      // encode entities
      var tag = $("<div>").addClass("tagtag-tag label"),
      tagContent = $("<span>").addClass("tagtag-tagcontent").text(s).appendTo(tag),
      tagClose = $("<span>").addClass("tagtag-tagclose").appendTo(tag),
      v = this.options.validator;

      if (v && !this.options.validator(s)) {
        tag.addClass("tagtag-taginvalid");
      } else {
        tag.addClass("tagtag-tagvalid");
      }

      this.input.before(tag);

      this._updateData();
      return tag;
    },


    /**
     * remove tag
     */
    _removeTag: function(tag) {
      tag.remove();
      this._updateData();
    },


    /**
     * move inputed content to tag
     */
    _inputToTag: function() {
      var s = this.input.val();
      
      if (s.length > 0) {
        var tag = this._insertTag(s);
        this.input.val('');
        if (this.options.onAddTag) {
          this.options.onAddTag.call(this.element, tag, s);
        }
      }
    },

    /**
     * onkeypress event handler
     */
    _onKeyPress: function(e) {
      if (this.options.delimiter.indexOf(String.fromCharCode(e.keyCode)) >= 0) {
        this._inputToTag();
        e.preventDefault();
      }
    },

    /**
     * onkeydown event handler
     * used for tab key
     */
    _onKeyDown: function(e) {
      if (e.keyCode == 0x09) {
        this._inputToTag();
        e.preventDefault();
      }
    },

    /**
     * onclick @ .tagtag-tagclose event handler
     */
    _onCloseClick: function(e) {
      var tag = $(e.target).closest(".tagtag-tag");
      this._removeTag(tag);
    },

    /***
     * onfocus
     */
    _onFocus: function(e) {
      this.container.addClass('focus');
    },

    /**
     * onblur event handler
     */
    _onBlur: function(e) {
      this._inputToTag();

      // remove invalid tags
      this.container.find(".tagtag-taginvalid").remove();

      this.container.removeClass('focus');
    }

  });


})(jQuery);
