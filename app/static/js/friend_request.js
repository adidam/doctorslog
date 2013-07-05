/**
 * Created with PyCharm.
 * User: ananth
 * Date: 6/1/13
 * Time: 1:04 PM
 * To change this template use File | Settings | File Templates.
 */
$(document).ready(function(){
    $("a.friend-request").click(function(){
        var url = $(this).attr("href");
        var id_d ='#'+$(this).parents("div.friend-request").attr("id");
        $.getJSON(url,function(data){
            $(id_d).html('<div class="requestStatus">'+data.data+'</div>');
            if(!window.location.hash){
                window.location.hash = 'a'
            }
        });return false;
    });
});

$(document).ready(function(){
    $("a.requestAccept").click(function(){
        var p_id = '#'+$(this).parent().attr("id");
        var url = $(this).attr("href");
        $.getJSON(
            url,
            function(data){
                $(p_id).html(data.data);
                window.location.reload();
            }
        );return false;
    });
});
