/**
 * Created with PyCharm.
 * User: ananth
 * Date: 2/26/13
 * Time: 8:02 PM
 * To change this template use File | Settings | File Templates.
 */
$(function(){
    $("div.comments_body").hide();
    $(".hide_list").hide();
    $(".show_list").click(function(e){
        var comments = $(this).parent().children().attr("id");
        $("#"+comments).slideDown('slow');
        var hide_list = $(this).parent().children(".hide_list");
        hide_list.show();
        $(this).hide();e.preventDefault();
    });
});

$(function(){
    $(".hide_list").click(function(){
        var comments = $(this).parent().children().attr("id");
        $("#"+comments).slideUp("slow");
        var show_list = $(this).parent().children(".show_list");
        show_list.show();
        $(this).hide();
        return false;
    });
});
