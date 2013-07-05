/**
 * Created with PyCharm.
 * User: ananth
 * Date: 5/3/13
 * Time: 8:22 PM
 * To change this template use File | Settings | File Templates.
 */

//a script to handle spam reports
$(function(){
    $(".report_post").click(function(){
        var form_container = $(this).parents(".post").find(".report_form_container");
        var message_container = $(this).parents(".post").find("span.report_message");
        var comment_form = $(this).parents(".post").find(".comment_submit");
        var url = $(this).attr('href');
        var link = $(this);
        $(form_container).load(
            url,
            function(){
                $(comment_form).hide();
                link.hide();
            }
        );return false;
    });
});

$(function(){
    $(".cancel_report").click(function(e){
        var comment_form = $(this).parents(".post").find(".comment_submit");
        $(this).parents(".post").find("a.report_post").show();
        $(comment_form).show();
        $(this).parents(".report_submit_form").remove();
        e.preventDefault();
    });
});
