/**
 * Created with PyCharm.
 * User: ananth
 * Date: 3/6/13
 * Time: 5:56 PM
 * To change this template use File | Settings | File Templates.
 */

$(function(){
    $("input[type='image']").click(function(){
        var url = $(this).attr('src');
        window.open(url);
        return false;
    });
});

$(function(){
    $(".subject,.subject_full").find("img").each(function(){
        $(this).css('cursor','pointer');
        $(this).click(function(){
            var url = $(this).attr('src');
            window.open(url);
            return false;
        });
    });
});
