/**
 * Created with PyCharm.
 * User: ananth
 * Date: 6/2/13
 * Time: 4:19 PM
 * To change this template use File | Settings | File Templates.
 */
$(function(){
    var location = window.location.href;
    if(window.location.hash){
        var hash = /#\S+/;
        window.location.href = window.location.href.replace(hash,'');
    }

    $(window).bind('hashchange',function(){
        if(!window.location.hash && location == window.location.href){
            window.location.reload();
        }
    });
});