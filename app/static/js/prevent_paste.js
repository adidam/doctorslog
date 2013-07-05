/**
 * Created with PyCharm.
 * User: ananth
 * Date: 5/28/13
 * Time: 9:34 AM
 * To change this template use File | Settings | File Templates.
 */
function preventPaste(elem){
    $(elem).live('paste',function(e){
        alert("Apologies,pasting text in this area is not allowed")
        e.preventDefault();
    });
}