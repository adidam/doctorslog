/**
 * Created with PyCharm.
 * User: ananth
 * Date: 5/2/13
 * Time: 7:44 PM
 * To change this template use File | Settings | File Templates.
 */

$(function(){
    $("#member_search").click(function(){
        $("#search_container").show();
        $("#search").load("/user_search/");
        $(this).hide();
        return false;
    });
});
$(function(){
    $("#close_search_link").click(function(){
        $("#search_container").hide();
        $("#member_search").show();
    });
});
