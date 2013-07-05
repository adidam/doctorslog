/**
 * Created with PyCharm.
 * User: ananth
 * Date: 2/12/13
 * Time: 9:27 PM
 * To change this template use File | Settings | File Templates.
 */

$(function(){
    $("img.com_menu").hide();
    $(".comment_items").mouseover(function(){
        $(this).children("img.com_menu").show();
    });
    $(".comment_items").mouseout(function(){
        $(this).children("img.com_menu").hide();
    });
});
