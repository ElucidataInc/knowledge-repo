$(document).ready(function() {
  $('#project_add_kr').change(function() {
    console.log("AB")
    console.log($(this).val())
    if ($(this).val() != 'Choose Project') {
      var pname = $(this).find('option:selected').text();
      console.log("DFE")
      console.log(pname)
      $.ajax({
          type: 'GET',
          url: "/ccbd24f370707c33603102adc7b77123/ajax/api/getkr",
          data: { pname: pname },
          contentType: 'application/json',
          dataType: 'json',
          success: function(response) {
            var options = [];
            for (var i=0, l=response.length; i<l; i++)
                options.push('<option value="'+response[i].name+'">'+response[i].name+'</option>');
            $('#kr_add_kr').html(options.join(''));
        }      
      });
    }
    else {
      $('select#kr_add_kr').html('').prop('disabled',true);
    }
  })
});


//   $('#searchbar').typeahead({
//     hint: false,
//     highlight: true,
//     minLength: 1
//   }, {
//     name: 'knowledge_posts',
//     limit: 20,
//     display: function(item) {
//         return item.title + " - " + item.author;
//     },
//     templates: {
//         empty: Handlebars.compile(
//             '<div class="tt-not-found">' +
//             'Unable to find any posts that match the current query' +
//             '</div>'
//         ),
//         suggestion: function(data) {
//             return '<p style="overflow-wrap:break-word">' + data.title + ' – <em>' + data.author + '</em></p>';
//         }
//     },
//     source: function(q, sync, async) {
//         $.ajax('/ccbd24f370707c33603102adc7b77123/ajax/index/typeahead?search=' + q, {
//             success: function(data, status) {
//                 async(JSON.parse(data));
//             }
//         })
//     }
//   });
// });
