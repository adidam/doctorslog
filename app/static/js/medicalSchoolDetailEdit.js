/**
 * Created with PyCharm.
 * User: ananth
 * Date: 5/14/13
 * Time: 10:45 PM
 * To change this template use File | Settings | File Templates.
 */
$(document).ready(function(){
    var form = $("#medSchool_edit_form");
    form.submit(function(){
        var loader = $(this).children("img");
        $(loader).show();
        $.post(
            form.attr('action'),
            form.serializeArray(),
            function(data){
                if(!data.is_valid){
                    $(loader).hide();
                    $("#form-fields-medSchool").html(data.html);
                    alert('Invalid entry,please try again..');
                }
                else{
                    $("#medSchool_wrapper").html(data.html);
                    $("#form-fileds-medSchool").empty();
                    $("#edit-medSchool").show();
                }
            }
        ).error(function(){alert("An error has occurred");$(loader).hide();});return false;
    });
});

$(document).ready(function(){
    $("#cancel-medSchool-edit").click("click",function(){
        $("#medSchool_wrapper").load("/ajax_settings #medSchool_wrapper/");
        $("#form-fields-medSchool").empty();
        $("#edit-medSchool").show();
        return false;
    });
});
