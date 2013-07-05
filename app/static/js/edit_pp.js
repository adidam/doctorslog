/**
 * Created with PyCharm.
 * User: ananth
 * Date: 12/6/12
 * Time: 7:38 PM
 * To change this template use File | Settings | File Templates.
 */


$(document).ready(function(){
    $("#profile_picture_edit_form").submit(function(){
        $(this).ajaxSubmit( /** here we are using jquery form plugin api,
             instead of default jquery form submission,because file fields cannot be serialized
             using .serializeArray() method */
            function(data){
                if(!data.is_valid){
                    $("#form-fields-pp").html(data.html);
                    alert('Invalid entry,please try again..');
                }
                else{
                    $("#profile_picture_wrapper").html(data.html);
                    $("#form-fields-pp").empty();
                    $("#edit-pp").show();
                }
            }
        );return false;
    });
});

$(document).ready(function(){
    $("#cancel-pp").click("click",function(){
        $("#profile_picture_wrapper").load("/ajax_settings #profile_picture_wrapper/");
        $("#form-fields-pp").empty();
        $("#edit-pp").show();
        return false;
    });
});

