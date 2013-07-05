/**
 * Created with PyCharm.
 * User: ananth
 * Date: 3/27/13
 * Time: 12:59 PM
 * To change this template use File | Settings | File Templates.
 */

var email_regex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
//reference for email regex  --> http://www.w3.org/TR/2012/CR-html5-20121217/forms.html#valid-e-mail-address

//intercepting some fields
$(function(){
    $('input#id_username').parent('li').attr('id','li_username');
    $('li#li_username').append('<br/><span class="suggestion" id="username_suggestion"></span>');
    $('input#id_first_name').parent('li').attr('id','li_first_name');
    $('li#li_first_name').append('<span class="suggestion" id="first_name_suggestion"></span>');
    $('input#id_middle_name').parent('li').attr('id','li_middle_name');
    $('li#li_middle_name').append('<span class="suggestion" id="middle_name_suggestion"></span>');
    $('input#id_last_name').parent('li').attr('id','li_last_name');
    $('li#li_last_name').append('<span class="suggestion" id="last_name_suggestion"></span>');
    $('input#id_email').parent('li').attr('id','li_email');
    $('li#li_email').append('<span class="suggestion" id="email_suggestion"></span>');
    $('input#id_alternate_email').parent('li').attr('id','li_alternate_email');
    $('li#li_alternate_email').append('<span class="suggestion" id="alternate_email_suggestion"></span>');
    $('input#id_Password').parent('li').attr('id','li_Password');
    $('li#li_Password').append('<span class="suggestion" id="Password_suggestion"></span>');
    $('input#id_Password2').parent('li').attr('id','li_Password2');
    $('li#li_Password2').append('<span class="suggestion" id="Password2_suggestion"></span>');
    $('select#id_speciality').parent('li').attr('id','li_speciality');
    $('li#li_speciality').append('<span class="suggestion" id="speciality_suggestion"></span>');
    $('input#id_registration_number').parent('li').attr('id','li_registration_number');
    $('li#li_registration_number').append('<span class="suggestion" id="registration_number_suggestion"></span>');
    $('#id_qualification').parent('li').attr('id','li_qualification');
    $('li#li_qualification').append('<span class="suggestion" id="qualification_suggestion"></span>');
    $('#id_medical_institute').parent('li').attr('id','li_medical_institute');
    $('li#li_medical_institute').append('<span class="suggestion" id="medical_institute_suggestion"></span>');
    $('#id_first_year_of_graduation').parent('li').attr('id','li_graduation_first_year');
    $('li#li_graduation_first_year').append('<span class="suggestion" id="graduation_first_year_suggestion"></span>')
});

//suggestions for first name,middle name,last name
function fn_check(elem){
    $(elem).bind('keyup focusout',function(){
        var str = $(elem).val();
        var span = $(this).parent().children('span.suggestion').attr("id");
        if(str.match(/^[a-zA-Z]+\s{0,}[a-zA-Z]*$/)){
            $('#'+span).text('');
        }
        else if(str==''){
            $('#'+span).text('');
        }
        else{
            $('#'+span).text('First name and optional middle name');
        }
    });
}

function ln_check(elem){
    $(elem).bind('keyup focusout',function(){
        var str = $(elem).val();
        var span = $(this).parent().children('span.suggestion').attr("id");
        if(str.match(/^\s*[a-zA-Z]+\s*$/)){
            $('#'+span).text('');
        }
        else if(str==''){
            $('#'+span).text('');
        }
        else{
            $('#'+span).text('First name and optional middle name');
        }
    });
}

//verify email address
function email_check(var1,var2){
    $(var1).bind('keyup focusout',function(){
        var email = $(var1).val();
        var span = $(this).parent().children('span.suggestion').attr("id");
        if(email.match(email_regex)){
            $('#'+span).text('');
        }
        else if(email==''){
            $('#'+span).text('');
        }
        else{
            $('#'+span).text('Enter a valid email address');
        }
    });

    $(var1).bind('focusout',function(){
        var email = $(var1).val();
        var span = $(this).parent().children('span.suggestion').attr("id");
        if(email.match(email_regex)){
            $('#'+span).text('');
        }
        else if(email==''){
            $('#'+span).text('');
        }
        else{
            $('#'+span).text('That may not be a valid email address');
        }
    });
}
//*************************************************************************
//verify password
$(function(){
    $("input#id_Password").bind('keyup',function(){
        var str = $(this).val();
        var span = $(this).parent().children('span.suggestion').attr("id");
        if(str.match(/^\S{6,20}$/)||str==''){
            $('#'+span).text('');
        }
        else{
            $('#'+span).text('Password should be between 6 and 20 characters,avoid spaces')
        }
    });
    $("input#id_Password2").bind('keyup',function(){
        var password1 = $('input#id_Password').val();
        var password2 = $(this).val();
        var span = $(this).parent().children('span.suggestion').attr("id");
        if(password1==password2){
            $('#'+span).text('');
        }
        else if(password2==''){
            $('#'+span).text('');
        }
        else{
            $('#'+span).text('Passwords should match');
        }
    });
    $("input#id_Password,input#id_Password2").bind('keyup focusout',function(){
        if($("input#id_Password").val()==''&&$("input#id_Password2").val()==''){
            var span1 = $("input#id_Password").parent().children('span.suggestion').attr("id");
            var span2 = $("input#id_Password2").parent().children('span.suggestion').attr("id");
            $('#'+span1).text('');
            $('#'+span2).text('');
        }
    });
});
// *************************************************************************

//select speciality
$(function(){
    $("#id_speciality").bind('focusin',function(){
        var span = $(this).parent().children('span.suggestion').attr("id");
        $('#'+span).text('Key down "Ctrl" or "Command" on a Mac,to select multiple options');
    });
    $("#id_speciality").bind('focusout',function(){
        var span = $(this).parent().children('span.suggestion').attr("id");
        $('#'+span).text('');
    });
});

$(function(){
    fn_check('input#id_first_name');
    ln_check('input#id_last_name');
    email_check('input#id_email','span#email_suggestion');
    email_check('input#id_alternate_email','span#alternate_email_suggestion');
});

function check(){
    $("#username_avail").bind('click',function(){
        var url = $(this).attr("href");
        var elem = $(this).parent().attr("id");
        $('#'+elem).load(
            url
        );return false;
    });
}

$(function(){
    $('input#id_username').bind('keyup change focusout',function(){
        var str = $(this).val();
        if(str==''){
            $('span#username_suggestion').text('');
        }
        else if(str.match(/^\w{6,20}$/)){
            $('span#username_suggestion').html(
                '<a id="username_avail" style="text-decoration:none" href="/username-availability/?q='
                    +str+
                    '">'+'check availability</a>').css(
                {'margin-right':'10px'}
            );
            $("#username_avail").bind('click',check());                }
        else{
            $('span#username_suggestion').text('alphanumerics only,between 6 and 20 characters,avoid spaces').css(
                {'color':'#FF7F2A','margin-right':'10px'}
            );
        }

        return false;
    });
});

$(function(){
    $('label[for="id_Password2"]').text('Retype Password:');
    $("#id_speciality").attr('size',3);
    $('input[type="text"],input[type="password"]').attr('size',40);
});
