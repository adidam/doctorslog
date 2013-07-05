/**
 * Created with PyCharm.
 * User: ananth
 * Date: 4/15/13
 * Time: 5:39 PM
 * To change this template use File | Settings | File Templates.
 */
$(function(){
    $(".edit_comment").hide();
    $(".delete_comment").hide();
    $(".comment_items").mouseover(function(){
        $(this).find(".edit_comment,.delete_comment").show();
    });
    $(".comment_items").mouseout(function(){
        $(this).find(".edit_comment,.delete_comment").hide();
    });
});
