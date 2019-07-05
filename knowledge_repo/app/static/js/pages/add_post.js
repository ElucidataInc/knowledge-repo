$(document).ready(function() {
  $('#project_add_kr').change(function() {
    if ($(this).val() != 'Choose Project') {
      var pname = $(this).find('option:selected').text();
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
