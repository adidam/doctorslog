/**
 * Created with PyCharm.
 * User: ananth
 * Date: 6/3/13
 * Time: 4:11 PM
 * To change this template use File | Settings | File Templates.
 */
function removeFriend(user,userFirstName){
    $(function(){
        $("a.removeFriend").click(function(){
            var url = $(this).attr("href");
            var div = $(this).parents(".relation");
            $.get(
                url,
                function(data){
                    if(data == ''){
                        div.html(data);
                        window.setTimeout(function(){location.reload()},1000);
                    }
                    if(data == 'friend'){
                        if(!confirm('Dr '+userFirstName+' will be removed from your friends list. Are you sure?')){
                            return false;
                        }
                        else{
                            $.get(
                                '/remove-friend/'+user+'/',
                                function(data){
                                    div.html(data);
                                    window.setTimeout(function(){location.reload()},2000);
                                }
                            );return false;
                        }
                    }
                }
            );return false;
        });
    });
}