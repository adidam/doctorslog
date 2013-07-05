
  function submitForm(editForm,formField,valueWrapper,editLink){
      var button = editForm.children('input:not([type="text"],[type="password"])');
      var loader= editForm.children('img');
      var wrapper = $(editForm).parents(".child_wrapper");
      $(button).hide();
      $(loader).show();
    $.post(
        editForm.attr('action'),
        editForm.serializeArray(),
        function(data){
            if(!data.is_valid || data.errorMsg){
                $(button).show();
                $(loader).hide();
                $(formField).html(data.html);
                if(data.errorMsg){
                    alert(data.errorMsg);
                }
            }
            else{
                $(valueWrapper).html(data.html);
                $(formField).empty();
                $(editLink).show();
                wrapper.removeClass("bgColor");
            }
        }
    ).error(function(){alert("An error has occurred");$(loader).hide()});
}
