/**
 * Created with PyCharm.
 * User: ananth
 * Date: 2/27/13
 * Time: 2:35 PM
 * To change this template use File | Settings | File Templates.
 */

$(function(){
    if($('input[name="share_with"]:checked').val()=='share with none'){
        $('.share').hide();
    }
    else{
        $('.to_draft').hide();
    }
    $('input[name="share_with"]').click(function(){
        if($(this).val()=='share with none'){
            $(".share").hide();
            $(".to_draft").show().css({
                'border': 'none',
                'background-color': '#5555FF',
                'color': '#FFFFFF',
                'margin-top': '20px',
                'padding': '3px 7px 3px 7px',
                'font-weight':'bold'
            });
            $(".to_draft").hover(
                function(){$(this).css('background-color','#2A2AFF')},
                function(){$(this).css('background-color','#5555FF')}
            )
        }
        else{
            $(".share").show().css({
                'border': 'none',
                'background-color': '#5555FF',
                'color': '#FFFFFF',
                'margin-top': '20px',
                'padding': '3px 7px 3px 7px',
                'font-weight':'bold'
            });
            $(".share").hover(
                function(){$(this).css('background-color','#2A2AFF')},
                function(){$(this).css('background-color','#5555FF')}
            );
            $(".to_draft").hide();
        }
    });
});

$(function(){
    if($('input[name="share_with"]:checked').val() == 'share with selected friends'){
        $("#select_friends, #id_selected_friends").show();
    }
    else{
        $("#select_friends, #id_selected_friends").hide();
    }
    $('input[name="share_with"]').click(function(){
        if($(this).val()=='share with selected friends'){
            $("#select_friends, #id_selected_friends").show();
        }
        else{
            $("#select_friends, #id_selected_friends").hide();
        }
    });
});
