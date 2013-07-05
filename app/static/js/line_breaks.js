/**
 * Created with PyCharm.
 * User: ananth
 * Date: 6/15/13
 * Time: 10:11 AM
 * To change this template use File | Settings | File Templates.
 */
function lineBreak(element){
    document.getElementById(element).onkeyup=keydown;
    function keydown (event) {
        if (event.target.id==element && event.which==13) {
            document.getElementById(element).innerHTML+="\n";
        }
    }
}

function lineBreaks(elem){
    $(elem).bind('keydown',function(event){
        if(event.which == 13){
            $(elem).innerHTML += '\n';
        }
    });
}