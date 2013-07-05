/**
 * Created with PyCharm.
 * User: ananth
 * Date: 6/18/13
 * Time: 7:55 AM
 * To change this template use File | Settings | File Templates.
 */
$(document).ready(function(){
    //THIS JAVASCRIPT FUNCTION DOES THE WORK AND RETURNS THE
    //STRING WITH HTML ANCHOR LINKS
    function replaceURLWithHTMLLinks(text) {
        //var exp = /(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;
        var exp = /(\b(https?|ftp|file:\/\/|www.|ftp)[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;
        return text.replace(exp,"<a href='$1'>$1</a>");
    }
    //THIS IS A JQUERY STATEMENT THAT GRABS A CHUNK OF
    //TEXT AND REPLACES IT WITH THE UPDATED STRING
    $("p.quickPost").each(function(i){
        var text = $(this).html();
        $(this).html(replaceURLWithHTMLLinks(text));
    });
});