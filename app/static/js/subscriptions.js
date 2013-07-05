/**
 * Created with PyCharm.
 * User: ananth
 * Date: 5/22/13
 * Time: 6:52 PM
 * To change this template use File | Settings | File Templates.
 */
$(function(){
    $("a.subscribe").click(function(e){
        var url = $(this).attr('href');
        var resp = $(this).parents("span.subscribe");

        resp.load(
            url,
            function(){
                window.setTimeout(function(){location.reload()},1000);
            }
        );return false;
    });
});
