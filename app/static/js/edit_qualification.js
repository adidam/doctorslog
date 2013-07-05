/**
 * Created with PyCharm.
 * User: ananth
 * Date: 5/17/13
 * Time: 10:58 AM
 * To change this template use File | Settings | File Templates.
 */
/**
 * Created with PyCharm.
 * User: ananth
 * Date: 12/3/12
 * Time: 11:01 PM
 * To change this template use File | Settings | File Templates.
 */

$(document).ready(function(){
    var form = $("#qualification_edit_form");
    form.submit(function(){
        $.post(
            form.attr('action'),
            form.serializeArray(),
            function(data){
                if(!data.is_valid){
                    $("#form-fields-qualification").html(data.html);
                    alert('Invalid entry,please try again..');
                }
                else{
                    $("#qualification_wrapper").html(data.html);
                    $("#form-fileds-qualification").empty();
                    $("#edit-qualification").show();
                }
            }
        );return false;
    });
});

$(document).ready(function(){
    $("#cancel-qualification").click("click",function(){
        $("#qualification_wrapper").load("/ajax_settings #qualification_wrapper/");
        $("#form-fields-qualification").empty();
        $("#edit-qualification").show();
        return false;
    });
});

