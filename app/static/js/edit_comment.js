/**
 * Created with PyCharm.
 * User: ananth
 * Date: 2/12/13
 * Time: 11:27 AM
 * To change this template use File | Settings | File Templates.
 */



$(function(){
    $(".edit_comment").click(function(){
        var div_id = $(this).parents(".comment_items").find(".comment_subject").attr("id");
        $(this).parents(".comment_items").find(".comment_opt_link").detach();
        var url = $(this).attr("href");
        $.getJSON(
            url,
            function(data){
               if(!window.location.hash){
                    window.location.hash = 'a';
                }
                $("#"+div_id).html(data.html);
            }
        );return false;
    });
});
