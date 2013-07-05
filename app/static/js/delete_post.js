/**
 * Created with PyCharm.
 * User: ananth
 * Date: 1/22/13
 * Time: 11:40 AM
 * To change this template use File | Settings | File Templates.
 */
//delete post
$(function(){
    $(".delete_post").click(function(){
        //ask for confirmation
        if(!confirm("Are you sure you want to delete this post?")){
            //prevent navigation if not cancelled
            return false;
        }
        //proceed if confirmed
        var loader = $(this).parents("#content_wrapper").find(".post-delete-loader");
        $(loader).show();
        var div = $(this).parents("#content_wrapper");
        var url = $(this).attr("href");
    var jqXHR =  $.get(
            url,
        function(data){
            div.html(data);
            if(!window.location.hash){
                window.location.hash = 'a';
            }
        }
    );jqXHR.always(function(){$(loader).hide()});
        jqXHR.error(function(){alert("An error has occurred")});
        return false;
    });
});


