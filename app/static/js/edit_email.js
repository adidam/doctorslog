/**
 * Created with PyCharm.
 * User: ananth
 * Date: 12/6/12
 * Time: 7:38 PM
 * To change this template use File | Settings | File Templates.
 */

$(document).ready(function(){
    var form = $("#email_edit_form");
    form.submit(function(){
        $.post(
            form.attr('action'),
            form.serializeArray(),
            function(data){
                if(!data.is_valid){
                    $("#form-fields-email").html(data.html);
                    alert('Invalid entry,please try again..');
                }
                else{
                    $("#email_wrapper").html(data.html);
                    $("#form-fileds-email").empty();
                    $("#edit-3").show();
                }
            }
        );return false;
    });
});

$(document).ready(function(){
    $("#cancel-3").click("click",function(){
        $("#email_wrapper").load("/ajax_settings #email_wrapper/");
        $("#form-fields-email").empty();
        $("#edit-3").show();
        return false;
    });
});

