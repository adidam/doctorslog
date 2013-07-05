/**
 * Created with PyCharm.
 * User: ananth
 * Date: 5/8/13
 * Time: 11:25 AM
 * To change this template use File | Settings | File Templates.
 */


$(function(){
    $(".previous_page,.next_page").click(function(){
        var url = $(this).attr("href");
        var div = $(this).parents(".post-wrapper");
        $.get(
            url,
            function(data){
                div.html(data)
            }
        );return false;
    });
});