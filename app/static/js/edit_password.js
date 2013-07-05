/**
 * Created with PyCharm.
 * User: ananth
 * Date: 12/6/12
 * Time: 10:29 PM
 * To change this template use File | Settings | File Templates.
 */

$(document).ready(function(){
    var form = $("#password_edit_form");
    form.submit(
        function(){
            $.post(
                form.attr('action'),
                form.serializeArray(),
                function(data){
                    if(!data.is_valid){
                        $("#form-fields-password").html(data.html);
                        alert(data.err);
                    }
                    else if(data.err){
                        $("#form-fields-password").html(data.html);
                        alert(data.err);
                    }
                    else{
                        $("#password_wrapper").html(data.html);
                        $("#form-fields-password").empty();
                        $("#edit-4").show();
                    }
                }
            );return false;
        }
    );
});

$(document).ready(function(){
    $("#cancel-4").click("click",function(){
        $("#password_wrapper").load("/ajax_settings #password_wrapper/");
        $("#edit-4").show();
        $("#form-fields-password").empty();
        return false;
    });
});