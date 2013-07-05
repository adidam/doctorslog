/**
 * Created with PyCharm.
 * User: ananth
 * Date: 4/15/13
 * Time: 5:02 PM
 * To change this template use File | Settings | File Templates.
 */
$(function(){
    $(".comment_submit").submit(function(e){
        var form_id = '#'+$(this).attr("id");
        $($(form_id).find("img.loader").show());
        var div_id = $(form_id).parents(".comments_container").children(".comments_body").attr("id");
        var form = $(form_id);
        var comment = '#'+form.find(".comment").attr("id");
        $.post(
            form.attr("action"),
            form.serializeArray(),
            function(data){
                if(data.is_valid){
                    if(!window.location.hash){
                        window.location.hash = 'a';
                    }
                    $($(form_id).find("img.loader").hide());
                    $("#"+div_id).append(data.html);
                    $(comment).val('');
                    $(comment).height(30);
                    //update comments
                    var num_comments_container = form.parents(".comments_container").children("a.show_list");
                    var num_comments_container_hide = form.parents(".comments_container").children("a.hide_list");
                    num_comments_container.html(data.num_comments+' Responses View Discussion');
                    if(num_comments_container_hide.is(':hidden') && num_comments_container.is(':hidden')){
                        num_comments_container_hide.html('Hide Discussion').show()
                    }
                }
                else{
                    alert("oops! too much or no text?");
                    $($(form_id).find("img.loader").hide());
                }

            }
        );return false;
    });
});

$(function(){
    $("textarea.comment").keydown(function(event){
        if(event.which == 13){
            var txt = $(this).val();
            if(txt!='' && txt.match(/\S+/)){
                $(this).parents("form.comment_submit").submit();
                return false;
            }
            else{
                return false;
            }
        }
    });
});
