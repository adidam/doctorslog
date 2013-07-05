/**
 * Created with PyCharm.
 * User: ananth
 * Date: 3/27/13
 * Time: 1:00 PM
 * To change this template use File | Settings | File Templates.
 */

var email_regex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
//reference for email regex  --> http://www.w3.org/TR/2012/CR-html5-20121217/forms.html#valid-e-mail-address

$(function(){
    $("input[type='submit']").bind('click',function(e){
        validate();
        if(!validate()){
            e.preventDefault();
        }
    });
});

//validate form
function validate(){
    var is_valid = true;
    var first_name = $("input#id_first_name").val();
    var span_first_name = $('#'+$("input#id_first_name").parent().children("span.suggestion").attr("id"));
    if(!first_name==''&&!first_name.match(/^[a-zA-Z]+$/)){
        span_first_name.text('*only alphabets,max of 20 letters,spaces not allowed');
        is_valid = false;
    }
    if(first_name==''){
        span_first_name.text('*This field is required');
        is_valid = false;
    }
    var middle_name = $("input#id_middle_name").val();
    var span_middle_name = $('#'+$("input#id_middle_name").parent().children("span.suggestion").attr("id"));
    if(!middle_name==''&&!middle_name.match(/^[a-zA-Z]+$/)){
        span_middle_name.text('*only alphabets,max of 20 letters,spaces not allowed');
        is_valid = false;
    }
    var last_name = $("input#id_last_name").val();
    var span_last_name = $('#'+$("input#id_last_name").parent().children("span.suggestion").attr("id"));
    if(!last_name==''&&!last_name.match(/^[a-zA-Z]+$/)){
        span_last_name.text('*only alphabets,max of 20 letters,spaces not allowed');
        is_valid = false;
    }
    if(last_name==''){
        span_last_name.text('*This field is required');
        is_valid = false;
    }
    var username = $("input#id_username").val();
    var span_username = $('#'+$("input#id_username").parent().children("span.suggestion").attr("id"));
    if(!username==''&&!username.match(/^\w{6,20}$/)){
        span_username.text('*alphanumerics only,between 6 and 20 characters,avoid spaces');
        is_valid = false;
    }
    if(username==''){
        span_username.text('*This field is required');
        is_valid = false;
    }
    var email = $("input#id_email").val();
    var span_email = $('#'+$("input#id_email").parent().children("span.suggestion").attr("id"));
    if(!email==''&&!email.match(email_regex)){
        span_email.text('*That may not be a valid email address');
        is_valid = false;
    }
    if(email==''){
        span_email.text('*This field is required');
        is_valid = false;
    }
    var alternate_email = $("input#id_alternate_email").val();
    var span_alternate_email = $('#'+$("input#id_alternate_email").parent().children("span.suggestion").attr("id"));
    if(!alternate_email==''&&!alternate_email.match(/^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/)){
        span_alternate_email.text('*That may not be a valid email address');
        is_valid = false;
    }
    var password = $("input#id_Password").val();
    var span_password = $('#'+$("input#id_Password").parent().children("span.suggestion").attr("id"));
    if(!password==''&&!password.match(/^\S{6,20}$/)){
        span_password.text('*password should be between 6 and 20,avoid spaces');
        is_valid = false;
    }
    if(password==''){
        span_password.text('*This field is required');
        is_valid = false;
    }
    var password2 = $("input#id_Password2").val();
    var span_password2 = $('#'+$("input#id_Password2").parent().children("span.suggestion").attr("id"));
    if(password!=password2&&!password2==''){
        span_password2.text('*passwords did not match');
        is_valid = false;
    }
    if(password2==''){
        span_password2.text('*This field is required');
        is_valid = false;
    }
    var registration_number = $("input#id_registration_number").val();
    var span_registration_number = $("#registration_number_suggestion");
    if(registration_number==''){
        span_registration_number.text('*This field is required');
        is_valid = false;
    }
    var qualification = $("#id_qualification").val();
    var span_qualification_suggestion = $("#qualification_suggestion");
    if(qualification == ''){
        span_qualification_suggestion.text('*This field is required');
        is_valid = false;
    }
    var medical_institute = $("#id_medical_institute").val();
    var span_medical_institute = $("#medical_institute_suggestion");
    if(medical_institute==''){
        span_medical_institute.text('*This field is required');
        is_valid = false;
    }
    var graduation_first_year = $("#id_first_year_of_graduation").val();
    var span_graduation_first_year = $("#graduation_first_year_suggestion");
    if(graduation_first_year==''){
        span_graduation_first_year.text('*This field is required');
        is_valid = false;
    }
    if(!$("select#id_speciality option").is(":selected")){
        $('#'+$("#id_speciality").parent("li").children("span.suggestion").attr("id")).text(
            '*Select one or more options'
        );
        is_valid = false;
    }
    return is_valid;
}
