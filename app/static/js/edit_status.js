/**
 * Created with PyCharm.
 * User: ananth
 * Date: 2/21/13
 * Time: 7:16 PM
 * To change this template use File | Settings | File Templates.
 */
$(function(){
    $(".edit_status_post").click(function(){
        var url = $(this).attr('href');
        var div = $(this).parents(".status_post_container").children(".status_post_subject");
        $(this).parent().hide();
        $(div).load(url,
            function(){
                if(!window.location.hash){
                    window.location.hash = 'a';
                }
            }
        );
        return false;
    });
});

/*$(function(){
    $(".edit_status_post").bind('click',function(){
        var url = $(this).attr('href');
        var div = $(this).parents(".status_post_subject").attr("id");
        $('#'+div).load(url);
        return false;
    });
});*/
