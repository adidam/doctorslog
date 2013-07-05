/**
 * Created with PyCharm.
 * User: ananth
 * Date: 5/14/13
 * Time: 6:48 PM
 * To change this template use File | Settings | File Templates.
 */
$(document).ready(function(){
    var form = $("#reg_no_edit_form");
    form.submit(function(){
        $.post(
            form.attr('action'),
            form.serializeArray(),
            function(data){
                if(!data.is_valid){
                    $("#form-fields-reg-no").html(data.html);
                    alert('Invalid entry,please try again..');
                }
                else{
                    $("#reg_no_wrapper").html(data.html);
                    $("#form-fileds-reg-no").empty();
                    $("#edit-reg-no").show();
                }
            }
        );return false;
    });
});

$(document).ready(function(){
    $("#cancel-reg-no").click("click",function(){
        $("#reg_no_wrapper").load("/ajax_settings #reg_no__wrapper/");
        $("#form-fields-reg-no").empty();
        $("#edit-reg-no").show();
        return false;
    });
});