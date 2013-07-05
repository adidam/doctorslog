/**
 * Created with PyCharm.
 * User: ananth
 * Date: 5/27/13
 * Time: 1:53 PM
 * To change this template use File | Settings | File Templates.
 */
$(function(){
    $(".subject,.subject_full,.status_post_subject").find("a").click(function(e){
        var url = $(this).attr("href");
        window.open(url);
        e.preventDefault();
    });
});
