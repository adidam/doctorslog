/**
 * Created with PyCharm.
 * User: ananth
 * Date: 5/17/13
 * Time: 10:08 PM
 * To change this template use File | Settings | File Templates.
 */
$(document).ready(function(){
    var form = $("#speciality_edit_form");
    form.submit(function(){
        var submit = $(this).children('input[type="submit"]');
        var loader = $(this).children("img");
        submit.hide();
        loader.show();
        $.post(
            form.attr('action'),
            form.serializeArray(),
            function(data){
                if(!data.is_valid){
                    $("#form-fields-speciality").html(data.html);
                    loader.hide();
                    submit.show();
                    alert('Select one or more choices and try again..');
                }
                else{
                    $("#speciality_wrapper").html(data.html);
                    $("#form-fileds-speciality").empty();
                    $("#edit-speciality").show();
                }
            }
        );return false;
    });
});

$(document).ready(function(){
    $("#cancel-speciality").click("click",function(){
        $("#speciality_wrapper").load("/ajax_settings #speciality_wrapper/");
        $("#form-fields-speciality").empty();
        $("#edit-speciality").show();
        return false;
    });
});


