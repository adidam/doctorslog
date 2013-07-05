/**
 * Created with PyCharm.
 * User: ananth
 * Date: 4/15/13
 * Time: 5:00 PM
 * To change this template use File | Settings | File Templates.
 */
$(document).ready(function(){
    $("input.input_submit[type='submit']").hide();
    $("textarea").keyup(function(){
        var id = $(this).attr("id");
        var str = $('#'+id).val();
        if ($("#"+id).val()!='' && str.match(/\S+/)){
           $("#"+id).parents("form.comment_submit").children("input.input_submit[type='submit']").show();
        }
        else{
            $("#"+id).parents("form.comment_submit").children("input.input_submit[type='submit']").hide();
        }
    });
});
