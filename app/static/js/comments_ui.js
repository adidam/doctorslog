/**
 * Created with PyCharm.
 * User: ananth
 * Date: 4/22/13
 * Time: 11:30 AM
 * To change this template use File | Settings | File Templates.
 */

$(function(){
    $(".comment_opt_link").click(function(e){
        var menu =  $(this).parents(".user_container").children(".comment_opt_container");
        $(menu).show();
        e.preventDefault();
    });
});
$(function(){
    $(document).mouseup(function(e){
        $(".comment_opt_container").hide();
        e.preventDefault();
    });
});

$(function(){
    $(".comment_opt_link").hide();
    $(".comment_items").mouseover(function(){
        $(this).find(".comment_opt_link").show();
    });
    $(".comment_items").mouseout(function(){
        $(this).find(".comment_opt_link").hide();
    });
});
