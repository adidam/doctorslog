/**
 * Created with PyCharm.
 * User: ananth
 * Date: 5/18/13
 * Time: 11:17 AM
 * To change this template use File | Settings | File Templates.
 */

 $(document).ready(function(){
    var form = $("#presentJob_edit_form");
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
                    $("#form-fields-presentJob").html(data.html);
                    submit.show();
                    loader.hide();
                    alert('Invalid entry,please try again..');
                }
                else{
                    $("#presentJob_wrapper").html(data.html);
                    $("#form-fileds-presentJob").empty();
                    $("#edit-presentJob").show();
                }
            }
        );return false;
    });
});

$(document).ready(function(){
    $("#cancel-presentJob").click("click",function(){
        $("#presentJob_wrapper").load("/ajax_settings #presentJob_wrapper/");
        $("#form-fields-presentJob").empty();
        $("#edit-presentJob").show();
        return false;
    });
});
