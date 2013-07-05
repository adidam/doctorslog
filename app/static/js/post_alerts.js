/**
 * Created with PyCharm.
 * User: ananth
 * Date: 4/4/13
 * Time: 11:24 PM
 * To change this template use File | Settings | File Templates.
 */

$(function(){
    var alert_link = $("span#notification_alerts");
    $.getJSON(
        '/post-alerts/',
        function(data){
            if(data.post_notifications > 0){
                $(alert_link).text(data.post_notifications);
            }
        }
    );return false;
});

$(function(){
    var alert_link = $("span#news_alerts");
    $.getJSON(
        '/news-alerts/',
        function(data){
            if(data.post_notifications > 0){
                $(alert_link).text(data.post_notifications);
            }
        }
    );return false;
});