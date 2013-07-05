/**
 * Created with PyCharm.
 * User: ananth
 * Date: 2/12/13
 * Time: 11:29 AM
 * To change this template use File | Settings | File Templates.
 */

/** delete comment */
$(function(){
    $(".delete_comment").click(function(){
        var div_id = $(this).parents(".comment_items").attr("id");
        var url = $(this).attr("href");
        var num_comments_container_show = $(this).parents(".comments_container").children(".show_list");
        var num_comments_container_hide = $(this).parents(".comments_container").children(".hide_list");
        $.getJSON(
            url,
            function(data){
                $('#'+div_id).html('');
                $('#'+div_id).remove();
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
