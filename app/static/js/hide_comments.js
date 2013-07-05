/**
 * Created with PyCharm.
 * User: ananth
 * Date: 5/7/13
 * Time: 12:17 PM
 * To change this template use File | Settings | File Templates.
 */

$(function(){
    $(".hide_comment").click(function(){
        var div = $(this).parents(".comment_items").attr("id");
        var url = $(this).attr("href");
        var num_comments_container_show = $(this).parents(".comments_container").find(".show_list");
        var num_comments_container_hide = $(this).parents(".comments_container").find(".hide_list");
        $.getJSON(
            url,function(data){
                $("#"+div).html(data.data);
                $("#"+div).remove();
                if(!window.location.hash){
                    window.location.hash = 'a';
                }
                //update number of comments
                if(data.num_comments == 0){
                    num_comments_container_show.html('');
                    num_comments_container_hide.html('');
                }
                else{
                    num_comments_container_show.html(data.num_comments+' Responses View Discussion');
                }
            }
        );return false;
    });
});
