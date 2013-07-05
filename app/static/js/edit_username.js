/**
 * Created with PyCharm.
 * User: ananth
 * Date: 12/3/12
 * Time: 11:01 PM
 * To change this template use File | Settings | File Templates.
 */

$(document).ready(function(){
    var form = $("#username_edit_form");
    form.submit(function(){
        $.post(
            form.attr('action'),
            form.serializeArray(),
            function(data){
                if(!data.is_valid){
                    $("#form-fields-username").html(data.html);
                    alert('Invalid entry,please try again..');
                }
                else{
                    $("#username_wrapper").html(data.html);
                    $("#form-fileds-username").empty();
                    $("#edit-username").show();
                }
            }
        );return false;
    });
});

$(document).ready(function(){
    $("#cancel-2").click("click",function(){
        $("#username_wrapper").load("/ajax_settings #username_wrapper/");
        $("#form-fields-username").empty();
        $("#edit-2").show();
        return false;
    });
});
