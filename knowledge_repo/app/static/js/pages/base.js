$(document).ready(function() {
    function getUrl(search_path, searchbar_val){
      search_path = search_path.slice(1);
      search_path_split = search_path.split('&');
      url = '/feed?filters=' + $('#searchbar').val();
      for(var i = 0;i < search_path_split.length;i ++)
      {
        query = search_path_split[i];
        if (query.slice(0,7) == 'filters')
          continue
        url = url + '&';
        url = url + query;
      }
      return url;
    }

    $("#searchbar")[0].setSelectionRange(1000, 1000);

    $('#searchbar').typeahead({
        hint: false,
        highlight: true,
        minLength: 1
    }, {
        name: 'knowledge_posts',
        limit: 20,
        display: function(item) {
            return item.title + " - " + item.author;
        },
        templates: {
            empty: Handlebars.compile(
                '<div class="tt-not-found">' +
                'Unable to find any posts that match the current query' +
                '</div>'
            ),
            suggestion: function(data) {
                return '<p style="overflow-wrap:break-word">' + data.title + ' – <em>' + data.author + '</em></p>';
            }
        },
        source: function(q, sync, async) {
            $.ajax('/ccbd24f370707c33603102adc7b77123/ajax/index/typeahead?search=' + q, {
                success: function(data, status) {
                    async(JSON.parse(data));
                }
            })
        }
    });


    $('#searchbar').bind('typeahead:select', function(obj, datum, name) {
        var search_args = window.location.search.split('&')
        var repo_val = ""
        for(var i=0;i<search_args.length;i++)
        {
            search_arg = search_args[i]
            if(search_arg[0]=='?')
                search_arg = search_arg.slice(1)
            if(search_arg.startsWith('repo'))
                repo_val = search_arg
        }
        window.location = '/ccbd24f370707c33603102adc7b77123/post/' + datum.path + '?' + repo_val;
    });

    $('#searchbar').keypress(function(event) {
      var keycode = (event.keyCode ? event.keyCode : event.which);
      if (keycode == '13') {
          window.location = getUrl(document.location.pathname, $('#searchbar').val());
        }
  });

    var padding = $('.tt-menu').outerWidth()
    $('.tt-menu').width($('#searchbar').width() + padding + "px")


    function update_panel_widths(panel_name) {
        if (window.matchMedia( "(min-width: 1200px)" ).matches){
            $(panel_name).width($(panel_name).parent().width());
            $(panel_name).css("position", "fixed");
        } else {
            $(panel_name).width('auto');
            $(panel_name).css("position", "relative");
        }
    }

    update_panel_widths('#panel-left');
    update_panel_widths('#panel-right');
    $(window).resize(update_panel_widths.bind(null, '#panel-left'));
    $(window).resize(update_panel_widths.bind(null, '#panel-right'));
});
