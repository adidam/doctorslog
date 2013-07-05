import re
import smtplib
#from unittest.test import loader
from uuid import uuid4
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User,check_password
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.mail import send_mail,EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse,Http404
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.cache import never_cache, cache_control
from app.forms import RegistrationForm,PasswordChangeForm, ProfilePictureForm, NameChangeForm,\
    UserNameChangeForm, EmailChangeForm, NewPostForm, FruitForm, UserSearch, GlobalShareSettingsForm, \
    InlineShareSettingsForm, NewPostModelForm, PostEditForm, CkEditorTest, CommentForm, StatusUpdateEditForm, \
    StatusCommentForm, SpamPostReportForm, SpamStatusPostReportForm, RegNoChangeForm, MedicalSchoolDetailEditForm, \
    QualificationEditForm, SpecialityEditForm, PresentJobEditForm,PreviousJobEditForm,ExpertiseEditForm,\
    OtherDetailsEditForm, GraduationYearEditForm,PGCollegeEditForm,PGYearEditForm
from app.models import UserProfile, ProfilePicture,Person,FriendRequests,GlobalShareSettings, UserPosts, Comments,\
    StatusUpdates, StatusComments, Speciality, ViewedUserPost, SpamPosts, SpamStatusPosts, SpamComments, SpamStatusComments, Subscriptions
from django.db.models import Q
from django.shortcuts import get_object_or_404
from PIL import Image,ImageOps
import os
from django.utils import simplejson
from datetime import datetime,timedelta
from ckeditor.views import get_image_files,get_media_url
from django.core.paginator import  Paginator,InvalidPage,EmptyPage
from django.template import Template,Context,loader
import settings
from dateutil import  tz

image_size = 150,150

#return offset for timedelta using users'(authenticated) timezone
def get_timezone_offset(auth_user):
    user_profile = UserProfile.objects.get(user=auth_user)
    offset = user_profile.timezone_offset.split('.')
    min = (int(offset[1])/float(10)) * 60
    hours,minutes = int(offset[0]),min
    return hours,minutes

#return offset value for timedelta accepting offset value
# from user registers,which is in string format
def get_timezone(offset):
    offset = offset.split('.')
    min = (int(offset[1])/float(10)) * 60
    hours,minutes = int(offset[0]),min
    return hours,minutes

def remove_repeats(first_list,new_list):
    for item in first_list:
        if item not in new_list:
            new_list.append(item)
    return new_list

def has_permission(post,user,posted_by):
    has_permission = False
    person = Person.objects.get(user = user)
    person_posted = Person.objects.get(user = posted_by)
    user_specialities = user.get_profile().speciality.split(',')
    post_relevance = post.relevance.all()
    if not post.posted_by == user:
        if not person.is_friend(person_posted):
            if not post.share_with == 'share with all':
                has_permission = False
            else:
                for s in user_specialities:
                    if s in post_relevance:
                        has_permission = True
                        break
        else:
            #if the users are friends
            if post.share_with == 'share with related friends':
                for s in post_relevance:
                    if s in user_specialities:
                        has_permission = True
                    else:
                        has_permission = False
            if post.share_with == 'share with selected friends':
                if person in post.selected_friends.all():
                    has_permission = True
    else:
        has_permission = True
    return  has_permission

def format_time(time):
    now = time
    #ignore microseconds
    return now - timedelta(microseconds=now.microsecond)

@login_required
def home_view(request):
    pic=""
    u=request.user
    try:
        p = ProfilePicture.objects.get(user=u)
        pic = p.photo.url
    except ObjectDoesNotExist:
        pass
    return render_to_response("index.html",
                              context_instance=(RequestContext(request,{'pic':pic})))


def my_page(request,person=None):
    if request.user.is_authenticated():
        try:
            u=User.objects.get(username=person)
        except ObjectDoesNotExist:
            return HttpResponseRedirect('/search_results/?name=%s' % person)
        user = request.user
        try:
            p=Person.objects.get(name=user)
        except ObjectDoesNotExist:
            raise Http404
        if user == u:
            user_posts = []
            for post in u.userposts_set.exclude(share_with = 'share with none'):
                post.can_be_commented = post.comments_allowed(user)
                post.comments_list = post.comments_set.all()
                post.num_comments = len(post.comments_list)
                user_posts.append(post)
            for status in u.statusupdates_set.all():
                status.can_be_commented = status.comments_allowed(user)
                status.statuscomments_list = status.statuscomments_set.all()
                status.num_comments = len(status.statuscomments_list)
                user_posts.append(status)
            sort_key = lambda x:x.date_posted
            user_posts.sort(key=sort_key,reverse=True)
            post_list = Paginator(user_posts,2)
            try:
                page = int(request.GET.get('page','1'))
            except  ValueError:
                page = 1
            try:
                user_posts = post_list.page(page)
            except (InvalidPage,EmptyPage):
                user_posts = post_list.page(post_list.num_pages)
            if request.is_ajax():
                html = render_to_string('mypage_ajax.html',{'user_posts':user_posts,'post_list':post_list,'u':u},
                    context_instance=RequestContext(request))
                return HttpResponse(html)
            else:
                return render_to_response('mypage.html',context_instance=RequestContext(request,
                    {'user_posts':user_posts,'post_list':post_list,'u':u}))
        else:
            u.is_friend = p.is_friend(u)
            u.friend_request_status = p.friend_request_status(u)
            u.sent_friend_request_status = p.received_request_status(u)
            try:
                s = Subscriptions.objects.filter(subscribed_by = user).get(subscribed_to = u)
                user.subscribed = 'subscribed'
            except ObjectDoesNotExist:
                user.subscribed = 'not subscribed'
            try:
                s = Subscriptions.objects.filter(subscribed_by = u).get(subscribed_to = user)
                u.subscribed = 'subscribed'
            except ObjectDoesNotExist:
                u.subscribed = 'not subscribed'
            return render_to_response('profileAbout.html',context_instance=RequestContext(request,
                    {'person':u}))
    #return HttpResponseRedirect('%s?next=%s' % (reverse(anonymous,args=[person]),person))
    return HttpResponseRedirect(reverse(anonymous,args=[person]))

def profile_posts(request,person=None):
    user = request.user
    p = Person.objects.get(name=user)
    try:
        u = User.objects.get(username=person)
    except ObjectDoesNotExist:
        raise Http404
    u.is_friend = p.is_friend(u)
    if p.is_friend(u):
        user_posts = []
        for post in u.userposts_set.exclude(share_with = 'share with none').exclude(share_with='share with selected friends'):
            if post.share_with == 'share with related friends':
                for usp in user.get_profile().speciality.split(','):
                    for sp in post.relevance.all():
                        if str(usp) == str(sp):
                            post.can_be_commented = post.comments_allowed(user)
                            post.num_comments = len(post.comments_set.all())
                            user_posts.append(post)
                            break
            else:
                post.can_be_commented = post.comments_allowed(user)
                post.num_comments = len(post.comments_set.all())
                user_posts.append(post)
        if u.userposts_set.filter(share_with='share with selected friends'):
            for post in u.userposts_set.filter(share_with='share with selected friends'):
                friends_list = []
                for person in post.selected_friends.all():
                    friends_list.append(person.get_user())
                    if user in friends_list:
                        post.can_be_commented = post.comments_allowed(user)
                        post.num_comments = len(post.comments_set.all())
                        user_posts.append(post)
        for status in u.statusupdates_set.all():
            if status.share_with == 'share with related friends':
                for usp in user.get_profile().speciality.split(','):
                    for sp in u.get_profile().speciality.split(','):
                        if str(usp) == str(sp):
                            status.can_be_commented = status.comments_allowed(user)
                            status.num_comments = len(status.statuscomments_set.all())
                            user_posts.append(status)
                            break
            else:
                status.can_be_commented = status.comments_allowed(user)
                status.num_comments = len(status.statuscomments_set.all())
                user_posts.append(status)
        sort_key = lambda x:x.date_posted
        user_posts.sort(key=sort_key,reverse=True)
        post_list = Paginator(user_posts,2)
        try:
            page = int(request.GET.get('page','1'))
        except  ValueError:
            page = 1
        try:
            user_posts = post_list.page(page)
        except (InvalidPage,EmptyPage):
            user_posts = post_list.page(post_list.num_pages)
        return render_to_response('profilePosts.html',context_instance=RequestContext(request,
                {'user_posts':user_posts,'post_list':post_list,'person':u}))
    else:
        p = Person.objects.get(name=user.username)
        u.friend_request_status = p.friend_request_status(u)
        u.sent_friend_request_status = p.received_request_status(u)
        user_posts = []
        posts = u.userposts_set.filter(share_with = 'share with all')
        status_posts = u.statusupdates_set.filter(share_with='share with all')
        for post in posts:
            if not post.is_spam(user):
                post.can_be_commented = post.comments_allowed(user)
                post.comments_list = post.comments_set.all()
                post.num_comments = len(post.comments_list)
                user_posts.append(post)
        for post in status_posts:
            if not post.is_spam(user):
                post.can_be_commented = post.comments_allowed(user)
                post.comments_list = post.statuscomments_set.all()
                post.num_comments = len(post.comments_list)
                user_posts.append(post)
        sort_key = lambda x:x.date_posted
        user_posts.sort(key=sort_key,reverse=True)
        post_list = Paginator(user_posts,2)
        p = Person.objects.get(name=u.username)
        u.num_friends = len(p.friends.all())
        try:
            page = int(request.GET.get('page','1'))
        except  ValueError:
            page = 1
        try:
            user_posts = post_list.page(page)
        except (InvalidPage,EmptyPage):
            user_posts = post_list.page(post_list.num_pages)
        try:
            s = Subscriptions.objects.filter(subscribed_by = user).get(subscribed_to = u)
            user.subscribed = 'subscribed'
        except ObjectDoesNotExist:
            user.subscribed = 'not subscribed'
        try:
            s = Subscriptions.objects.filter(subscribed_by = u).get(subscribed_to = user)
            u.subscribed = 'subscribed'
        except ObjectDoesNotExist:
            u.subscribed = 'not subscribed'
        return render_to_response('profilePosts.html',context_instance=RequestContext(request,
                {'person':u,'user_posts':user_posts,'post_list':post_list}))



def anonymous(request,person):
    try:
        u = User.objects.get(username=person)
    except ObjectDoesNotExist:
        query_set = User.objects.filter(Q(username__istartswith = person)|Q(first_name__istartswith = person)|
                                        Q(last_name__istartswith=person))
        if query_set:
            u = User.objects.get(username=query_set[0])
            return render_to_response('anonymousPage.html',context_instance=RequestContext(request,
                    {'person':u,'next':'/%s/' % u.username,'guess':True}))
        else:
            return HttpResponseRedirect('/login/')
    return render_to_response('anonymousPage.html',context_instance=RequestContext(request,
            {'person':u,'next':'/%s/' % u.username,'guess':False}))

#a basic user registration view that displays a form and redirects to success page
def sign_up(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            CD = form.cleaned_data
            u = User(first_name=CD['first_name'],
                     last_name=CD['last_name'],
                     username=CD['username'],
                     email=CD['email'],
                     #password=CD['Password'],
                    )
            #needed to explicitly call set_password to pass validation,don't know why
            u.set_password(CD['Password'])
            u.save()
            user_profile = UserProfile(
                qualification = CD['qualification'],
                graduation_medical_institute = CD['medical_institute'],
                graduation_first_year = CD['first_year_of_graduation'],
                post_graduation_medical_institute = CD.get('post_graduation_medical_institute',''),
                post_graduation_first_year = CD.get('first_year_of_post_graduation',''),
                super_speciality_medical_institute = CD.get('super_speciality_from',''),
                super_speciality_first_year = CD.get('first_year_of_super_speciality',''),
                timezone_offset = CD.get('timezone_offset',''),
                country = CD['country'],
                speciality = ','.join(CD['speciality']),
                password_update_date = format_time(datetime.utcnow()),
                checked_notifications_on = format_time(
                    datetime.utcnow()+timedelta(
                        hours = get_timezone(CD.get('timezone_offset',0))[0],
                        minutes = get_timezone(CD.get('timezone_offset',0))[1]
                    )
                ),
                checked_news_on = format_time(datetime.utcnow()),
                checked_requests_on = format_time(datetime.utcnow()),
                user = u,
                )
            user_profile.save()
            #save a person object,a model to manage friends' relations
            Person.objects.create(name=u.username)
            #save GlobalShareSettings object that defaults to 'share with all'
            GlobalShareSettings.objects.create(user=u)
            return HttpResponseRedirect('/success/')
        else:
            return render_to_response('sign_up.html',context_instance=RequestContext(request,
                    {'form':form}))
    else:
        form = RegistrationForm()
    return render_to_response('sign_up.html',
        context_instance=RequestContext(request,
            {'form':form})
        )

@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/login/')


@login_required
def settings_view(request):
    u = request.user
    up = u.get_profile()
    return render_to_response('settings/settings.html',
        context_instance=RequestContext(request,{'u':u,'up':up}))

#view to change password
@login_required
def password_reset_view(request):
    u = request.user
    up = u.get_profile()
    errors = []
    if request.method == "POST":
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            CD = form.cleaned_data
            if CD['new_password'] == CD['new_password_again']:
                if check_password(CD['password'],u.password):
                    u.set_password(CD['new_password'])
                    u.save()
                    return render_to_response('settings/settings.html',
                        context_instance=RequestContext(request,{'u':u,
                                                                 'up':up}
                            )
                        )
                else:
                    errors.append('That is an incorrect password,Try again')
            else:
                errors.append('Passwords did not match try again')
    else:
        form = PasswordChangeForm()
    return render_to_response('settings/password_reset.html',
        context_instance=RequestContext(request,{'u':u,
                                                 'up':up,
                                                 'form':form,
                                                 'errors_list':errors}
        )
    )

#a generic view to edit profile settings
@login_required
def profile_settings_view(request,param,edit_form,template_name):
    u = request.user
    up = u.get_profile()
    if request.method == "POST":
        form = edit_form(request.POST)
        if form.is_valid():
            CD = form.cleaned_data
            if param == 'first_name':
                u.first_name = CD[param]
                u.save()
            elif param == 'last_name':
                u.last_name = CD[param]
                u.save()
            elif param == 'username':
                u.username = CD[param]
                u.save()
            elif param == 'email':
                u.email = CD[param]
                u.save()
            elif param == 'reg_no':
                up.registration_number = CD[param]
                up.save()
            elif param == 'expertise':
                up.expertise = CD[param]
                up.save()
            return HttpResponseRedirect('/settings/')
    else:
        form = edit_form()
    return render_to_response(template_name,
        context_instance=RequestContext(request,{'u':u,'up':up,'form':form,}
        )
    )

#a view to set or edit profile picture,re-sizes uploaded image, also deletes older image
@login_required
def profile_picture(request):
    u = request.user
    up = u.get_profile()
    try:
        p = ProfilePicture.objects.get(user=u)
        os.remove(p.photo.path)
        p.delete()
    except ObjectDoesNotExist:
        pass
    if request.method == "POST":
        form = ProfilePictureForm(request.POST,request.FILES)
        if form.is_valid():
            ins = form.save(commit=False)
            ins.user = u
            ins.save()
            im = Image.open(ins.photo.path)
            im.thumbnail(image_size,Image.ANTIALIAS)
            im.save(ins.photo.path)
        return HttpResponseRedirect('/settings/')
    else:
        form = ProfilePictureForm()
    return render_to_response('settings/profile_picture.html',
        context_instance=RequestContext(request,{'form':form,
                                                 'u':u,'up':up}
        )
    )

#testing ajax
def ajax_test(request):
    if request.is_ajax():
        message = "This is an Ajax message"
    else:
        message = "Ajax error"
    return render_to_response("ajax.html",
        context_instance=RequestContext(request,{'message':message}))

#ajax settings view
# following views are writen with ajax in mind
# a base settings page
def ajax_settings(request):
    u = request.user
    try:
        p=ProfilePicture.objects.get(user=u)
        profile_picture = p
    except ObjectDoesNotExist:
        profile_picture=None
        pass
    return render_to_response('AjaxSettings/base_settings.html',
        context_instance=RequestContext(request,{
            'first_name':u.first_name,
            'last_name':u.last_name,
            'username':u.username,
            'email':u.email,
            'password_update_date':u.get_profile().password_update_date,
            'profile_picture':profile_picture
        }
        )
    )

def edit_name(request):
    u = request.user
    if request.method == "POST":
        form = NameChangeForm(request.POST)
        if form.is_valid():
            CD = form.cleaned_data
            u.first_name = CD['first_name']
            u.last_name = CD['last_name']
            u.save()
            html = render_to_string('AjaxSettings/name_edit.html',
                    {'first_name':u.first_name,'last_name':u.last_name},
                context_instance=RequestContext(request))
        else:
            html = render_to_string('AjaxSettings/name_edit_form.html',
                    {'form':form},context_instance=RequestContext(request))

    else:
        form = NameChangeForm()
        return render_to_response('AjaxSettings/name_edit_form.html',
            context_instance=RequestContext(request,{'form':form}))
    response = simplejson.dumps({'html':html,'is_valid':form.is_valid()})
    return HttpResponse(response,status=200,mimetype='application/json')

def edit_username(request):
    u = request.user
    if request.method == "POST":
        form = UserNameChangeForm(request.POST)
        if form.is_valid():
            if 'passwordForUsername' in request.POST and request.POST['passwordForUsername']:
                entered_password = request.POST['passwordForUsername']
                is_correct = check_password(entered_password,u.password)
                if is_correct:
                    #check if that username has already been taken
                    try:
                        u_name = User.objects.get(username=request.POST['username'])
                    except ObjectDoesNotExist:
                        pass
                    else:
                        if u_name.username != u.username:
                            error = 'Sorry,that username has already been taken,try another'
                            html = render_to_string('AjaxSettings/username_edit_form.html',
                                    {'form':form},context_instance=RequestContext(request))
                            response = simplejson.dumps({'html':html,'is_valid':form.is_valid(),'errorMsg':error})
                            return HttpResponse(response,status=200,mimetype='application/json')
                    CD = form.cleaned_data
                    u.username = CD['username']
                    u.save()
                    html = render_to_string('AjaxSettings/username_edit.html',
                        {'username':u.username},context_instance=RequestContext(request))
                    response = simplejson.dumps({'html':html,'is_valid':form.is_valid()})
                    return HttpResponse(response,status=200,mimetype='application/json')
                else:
                    error = 'Password may not be correct'
            else:
                error = 'Please enter your password'
        else:
            error = 'Invalid entry for username'
        html = render_to_string('AjaxSettings/username_edit_form.html',
            {'form':form},context_instance=RequestContext(request))
        response = simplejson.dumps({'html':html,'is_valid':form.is_valid(),'errorMsg':error})
        return HttpResponse(response,status=200,mimetype='application/json')
    else:
        form = UserNameChangeForm()
        return render_to_response('AjaxSettings/username_edit_form.html',
            context_instance=RequestContext(request,{'form':form}))


def edit_email(request):
    u = request.user
    if request.method == "POST":
        form = EmailChangeForm(request.POST)
        if form.is_valid():
            CD = form.cleaned_data
            u.email = CD['email']
            u.save()
            html = render_to_string('AjaxSettings/email_edit.html',
                    {'email':u.email},context_instance=RequestContext(request))
        else:
            html = render_to_string('AjaxSettings/email_edit_form.html',
                    {'form':form},context_instance=RequestContext(request))
    else:
        form = EmailChangeForm()
        return render_to_response('AjaxSettings/email_edit_form.html',
            context_instance=RequestContext(request,{'form':form}))
    response = simplejson.dumps({'html':html,'is_valid':form.is_valid()})
    return HttpResponse(response,status=200,mimetype='application/json')

def edit_password(request):
    err = ''
    u = request.user
    password_update_date = u.get_profile().password_update_date
    if request.method == "POST":
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            CD = form.cleaned_data
            if check_password(CD['password'],u.password):
                if CD['new_password'] == CD['new_password_again']:
                    u.set_password(CD['new_password'])
                    u.save()
                    u.get_profile().password_update_date = format_time(datetime.utcnow()+timedelta(
                        hours = get_timezone_offset(u)[0],
                        minutes = get_timezone_offset(u)[1]
                    ))
                    html = render_to_string('AjaxSettings/password_edit.html',{'password_update_date':password_update_date},
                        context_instance=RequestContext(request))
                else:
                    html = render_to_string('AjaxSettings/password_edit_form.html',
                            {'form':form},context_instance=RequestContext(request))
                    err = 'Passwords did not match'
            else:
                html = render_to_string('AjaxSettings/password_edit_form.html',
                        {'form':form},context_instance=RequestContext(request))
                err = 'Invalid password'
        else:
            html = render_to_string('AjaxSettings/password_edit_form.html',
                {'form':form,},context_instance=RequestContext(request))
            err = 'All fields are required,\npassword should be at least 6 characters'
    else:
        form = PasswordChangeForm()
        return render_to_response('AjaxSettings/password_edit_form.html',
            context_instance=RequestContext(request,{'form':form}))
    response = simplejson.dumps({'html':html,'is_valid':form.is_valid(),'err':err})
    return HttpResponse(response,status=200,mimetype='application/json')

def edit_medical_school_detail(request):
    u=request.user
    if request.method == "POST":
        form = MedicalSchoolDetailEditForm(request.POST)
        if form.is_valid():
            CD = form.cleaned_data
            up = UserProfile.objects.get(user=u)
            up.graduation_medical_institute = CD['medical_school']
            up.save()
            html = render_to_string("AjaxSettings/medicalSchoolEdit.html",
                    {},context_instance=RequestContext(request))
        else:
            html = render_to_string("AjaxSettings/medicalSchoolEditForm.html",
                    {'form':form},context_instance=RequestContext(request))
    else:
        form = MedicalSchoolDetailEditForm()
        return render_to_response("AjaxSettings/medicalSchoolEditForm.html",
            context_instance=RequestContext(request,{'form':form}))
    response = simplejson.dumps({'html':html,'is_valid':form.is_valid()})
    return HttpResponse(response,status=200,mimetype='application/json')

def edit_graduation_year(request):
    u = request.user
    if request.method == "POST":
        form = GraduationYearEditForm(request.POST)
        if form.is_valid():
            CD = form.cleaned_data
            up = UserProfile.objects.get(user=u)
            up.graduation_first_year = CD['graduation_year']
            up.save()
            html = render_to_string('AjaxSettings/graduationYearEdit.html',{},
            context_instance=RequestContext(request))
        else:
            html = render_to_string('AjaxSettings/graduationYearEditForm.html',{'form':form},
            context_instance=RequestContext(request))
    else:
        form = GraduationYearEditForm()
        return render_to_response('AjaxSettings/graduationYearEditForm.html',context_instance=RequestContext(request,
        {'form':form}))
    response = simplejson.dumps({'html':html,'is_valid':form.is_valid()})
    return HttpResponse(response,status=200,mimetype='application/json')

def edit_qualification(request):
    u = request.user
    if request.method == "POST":
        form = QualificationEditForm(request.POST)
        if form.is_valid():
            CD = form.cleaned_data
            up = UserProfile.objects.get(user=u)
            up.qualification = CD['qualification']
            up.save()
            html = render_to_string('AjaxSettings/qualificationEdit.html',
                    {},context_instance=RequestContext(request))
        else:
            html = render_to_string("AjaxSettings/qualificationEditForm.html",
                    {'form':form},context_instance=RequestContext(request))
    else:
        form = QualificationEditForm()
        return render_to_response("AjaxSettings/qualificationEditForm.html",
            context_instance=RequestContext(request,{'form':form}))
    response = simplejson.dumps({'html':html,'is_valid':form.is_valid()})
    return HttpResponse(response,status=200,mimetype='application/json')

#a view to set/edit profile picture
def edit_profile_picture(request):
    u = request.user
    if request.method == "POST":
        form = ProfilePictureForm(data=request.POST,files=request.FILES)
        if form.is_valid():
            try:
                p=ProfilePicture.objects.get(user=u)
                os.remove(p.photo.path)
                p.delete()
            except ObjectDoesNotExist:
                pass
            ins = form.save(commit=False)
            ins.user = u
            ins.pp_update_date = format_time(datetime.utcnow()+timedelta(
                hours = get_timezone_offset(u)[0],
                minutes = get_timezone_offset(u)[1]
            ))
            ins.save()
            im = Image.open(ins.photo.path)
            #image is cropped to 150,150 size, from the center
            imageFit = ImageOps.fit(im,image_size,Image.ANTIALIAS)
            imageFit.save(ins.photo.path)
            html = render_to_string('AjaxSettings/profile_picture_edit.html',
                    {'pp_update_date':ins.pp_update_date},context_instance=RequestContext(request))
        else:
            html = render_to_string('AjaxSettings/profile_picture_edit_form.html',
                    {'form':form},context_instance=RequestContext(request))
    else:
        form = ProfilePictureForm()
        html = render_to_string('AjaxSettings/profile_picture_edit_form.html',
                {'form':form},context_instance=RequestContext(request))
    response = simplejson.dumps({'html':html,'is_valid':form.is_valid()})
    return HttpResponse(response,status=200,mimetype='application/json')

def edit_speciality(request):
    u = request.user
    if request.method == "POST":
        form = SpecialityEditForm(request.POST)
        if form.is_valid():
            CD = form.cleaned_data
            up = UserProfile.objects.get(user=u)
            up.speciality = ','.join(CD['speciality'])
            up.save()
            html = render_to_string("AjaxSettings/specialityEdit.html",
                    {},context_instance=RequestContext(request))
        else:
            html = render_to_string("AjaxSettings/specialityEditForm.html",
                    {'form':form},context_instance=RequestContext(request))
    else:
        form = SpecialityEditForm()
        return render_to_response("AjaxSettings/specialityEditForm.html",
            context_instance=RequestContext(request,{'form':form}))
    response = simplejson.dumps({'html':html,'is_valid':form.is_valid()})
    return HttpResponse(response,status=200,mimetype='application/json')

def edit_profile_details(request,editForm,template_edit,template_edit_form,param):
    u = request.user
    Form = eval(editForm)
    if request.method =="POST":
        form = Form(request.POST)
        if form.is_valid():
            CD = form.cleaned_data
            up = UserProfile.objects.get(user=u)
            setattr(up,param,CD[param])
            up.save()
            html = render_to_string(template_edit,{},context_instance=RequestContext(request))
        else:
            html = render_to_string(template_edit_form,
                    {'form':form},context_instance=RequestContext(request))
    else:
        form = Form()
        return render_to_response(template_edit_form,
            context_instance=RequestContext(request,{'form':form}))
    response = simplejson.dumps({'html':html,'is_valid':form.is_valid()})
    return HttpResponse(response,status=200,mimetype='application/json')

#a view to display friends
def friends_display(request):
    u = request.user
    friends_list = []
    #get the person object for the user
    p = Person.objects.get(name=u)
    #get friends query set for that person object
    friends = p.friends.all()
    if friends:
        #iterate through friends query set
        for friend in friends:
            #get user objects
            friends_list.append(friend.get_user()) #now friends_list is a list of actual user objects
    return render_to_response('friends_list.html',
        context_instance=RequestContext(request,
                {'friends_list':friends_list}))

#testing django-selectable
def fruit_search(request):
    form = FruitForm()
    return render_to_response('fruit_search.html',
        context_instance=RequestContext(request,{'form':form}))

#user search
def user_search(request):
    form = UserSearch()
    return render_to_response('user_search.html',
        context_instance=RequestContext(request,{'form':form}))

#a pretty basic search query,should be more robust
@cache_control(no_cache=True,no_store=True)
def search_results(request):
    u = request.user
    search_results = []
    p = Person.objects.get(name=u.username)
    if 'name' in request.GET and request.GET['name']:
        name = request.GET['name']
        name = name.lower().split()
        if len(name) >= 2 and name[0].upper() == 'DR':
            name = name[1:]
            if len(name) > 1:
                query_set = User.objects.filter(first_name__istartswith = name[0]).filter(last_name__istartswith = name[1])
            else:
                query_set = User.objects.filter(Q(username__istartswith=name[0])|
                                                Q(first_name__istartswith=name[0]) | Q(last_name__istartswith=name[0]))
        else:
            query_set = User.objects.filter(Q(username__istartswith=name[0])|
                                            Q(first_name__istartswith=name[0]) | Q(last_name__istartswith=name[0]))
        if query_set:
            for user in query_set:
                user.is_friend = p.is_friend(user)
                user.friend_request_status = p.friend_request_status(user)
                user.sent_friend_request_status = p.received_request_status(user)
                search_results.append(user)
                try:
                    Subscriptions.objects.filter(subscribed_by = u).get(subscribed_to = user)
                    user.subscribed_by = 'subscribed'
                except ObjectDoesNotExist:
                    user.subscribed_by = 'not subscribed'
                try:
                    Subscriptions.objects.filter(subscribed_by = user).get(subscribed_to = u)
                    user.subscribed = 'subscribed'
                except  ObjectDoesNotExist:
                    user.subscribed = 'not subscribed'
        #exclude user from search results
        if u in search_results:
            search_results.remove(u)
    return render_to_response('user_search_results.html',
        context_instance=RequestContext(request,{'search_results':search_results}))

#a view to handle sent friend requests
def friend_request(request,member):
    try:
        m = User.objects.get(username=member)
    except ObjectDoesNotExist:
        return Http404
    u = request.user
    p = Person.objects.get(name=member)
    if not p.is_friend(u):
        try:
            FriendRequests.objects.get(sent_to=u,sent_by=m,status='pending')
            message = 'Ahoy,you might have just received a friend request from Dr %s'%m.first_name.capitalize()+\
                      ' please refresh page'
            response = simplejson.dumps({'data':message})
            return HttpResponse(response,mimetype='application/json',status=200)
        except ObjectDoesNotExist:
            pass
        try:
            FriendRequests.objects.get(sent_to=m,sent_by=u,status='pending')
            message = 'Friend Request already sent'
        except ObjectDoesNotExist:
            FriendRequests.objects.create(sent_to=m,sent_by=u,status='pending')
            message = 'Friend Request Sent'
    else:
        message = None
    response = simplejson.dumps({'data':message})
    return HttpResponse(response,mimetype='application/json',status=200)

#view to display friend request alerts
def request_alerts(request):
    u = request.user
    fr = u.received_requests.filter(status='pending')
    num_requests = len(fr)
    response = simplejson.dumps({'data':num_requests})
    return HttpResponse(response,mimetype='application/json',status=200)

#view to handle friend request details
def request_details(request):
    new_requests = []
    ignored_requests = []
    u = request.user
    fr = u.received_requests.filter(status='pending')
    fr_ignored = u.received_requests.filter(status='ignored')
    for item in fr:
        new_requests.append(item.sent_by)
    for item in fr_ignored:
        ignored_requests.append(item.sent_by)
    if request.is_ajax():
        html = render_to_string('friend_request_details.html',{'new_requests':new_requests,'ignored_requests':ignored_requests},
        context_instance=RequestContext(request))
        response = simplejson.dumps({'html':html})
        return HttpResponse(response,status=200,mimetype='application/json')
    return render_to_response('friend_request_details1.html',
        context_instance=RequestContext(request,{'new_requests':new_requests,'ignored_requests':ignored_requests}))

def request_accept(request,member):
    u1 = request.user
    u2 = User.objects.get(username=member)
    try:
        #a friend request object can have only one sender and one recipient
        fr = u1.received_requests.get(sent_by = u2)
    except ObjectDoesNotExist:
        raise Http404
    p1 = Person.objects.get(name=u1.username)
    p2 = Person.objects.get(name=u2.username)
    p1.friends.add(p2)
    #remove subscriptions in either direction because the users are friends now
    try:
        s1 = Subscriptions.objects.filter(subscribed_by=u1).get(subscribed_to=u2)
        s1.delete()
    except ObjectDoesNotExist:
        pass
    try:
        s2 = Subscriptions.objects.filter(subscribed_by=u2).get(subscribed_to=u1)
        s2.delete()
    except ObjectDoesNotExist:
        pass
    fr.delete()
    response = simplejson.dumps({'data':'Friend'})
    return HttpResponse(response)

def request_ignore(request,member):
    u1 = request.user
    u2 = User.objects.get(username=member)
    try:
        fr = u1.received_requests.get(sent_by=u2)
    except ObjectDoesNotExist:
        raise Http404
    fr.status = 'ignored'
    fr.save()
    return HttpResponseRedirect('/request-details/')

def remove_friend(request,member):
    u1 = request.user
    p1 = Person.objects.get(name=u1.username)
    try:
        u2  = User.objects.get(username=member)
        p2 = Person.objects.get(name=u2.username)
        #in a rare case,if the other user has already removed this user from the friends list,
        #just refresh,of course this is called by ajax,we don't return any response,the jquery code
        #refreshes the page after a set time out of 1 second !
        if not p1.is_friend(u2):
            return HttpResponse('')
        p1.friends.remove(p2)
    except ObjectDoesNotExist:
        raise Http404
    try:
        fr = FriendRequests.objects.filter\
            (Q(sent_by = u1,sent_to = u2)|Q(sent_by=u2,sent_to=u1)).get(status='accepted')
    except ObjectDoesNotExist:
        pass
    else:
        fr.delete()
    return HttpResponse('<span style="color:red;">Dr %s has been removed from your friends list</span>' % u2.first_name.capitalize())

def check(request):
    form = GlobalShareSettingsForm(request.user)
    return render_to_response('check.html',context_instance=
    RequestContext(request,{'form':form}))


#testing tinymce
def new_post(request):
    u = request.user
    try:
        p=Person.objects.get(name=u)
    except ObjectDoesNotExist:
        raise  Http404
    form = NewPostModelForm(u,p)
    return render_to_response('new_post.html',
        context_instance=RequestContext(request,{'form':form}))

def inline_share_settings(request):
    u = request.user
    form1 = InlineShareSettingsForm(u)
    return render_to_response('inline_share_Settings.html',
        context_instance=RequestContext(request,{'form1':form1}))

def privacy_settings(request):
    u = request.user
    share_with = u.globalsharesettings.share_with
    return render_to_response('privacy_settings.html',context_instance=RequestContext(request,
            {'share_with':share_with}))

def global_share_settings(request):
    u = request.user
    if request.method == "POST":
        form = GlobalShareSettingsForm(u,request.POST)
        if form.is_valid():
            CD = form.cleaned_data
            g = GlobalShareSettings.objects.get(user=u)
            g.share_with = CD['share_with']
            g.save()
        return HttpResponseRedirect('/privacy_settings/')
    else:
        form = GlobalShareSettingsForm(u)
    return render_to_response('global_share_Settings.html',context_instance=RequestContext(request,
            {'form':form}))

#this function is not used,will be removed later
def new_post_view(request):
    u = request.user
    if request.method == "POST":
        form = NewPostForm(u,request.POST)
        if form.is_valid():
            CD = form.cleaned_data
            new_post = UserPosts(
                title = CD['title'],
                subject = CD['subject'],
                relevance = ','.join(CD['relevance']),
                mark_as = CD['mark_as'],
                share_with = CD['share_with']
            )
            new_post.posted_by = u
            new_post.date_posted = format_time(datetime.utcnow())
            new_post.save()
            return HttpResponseRedirect('/home/')
        return render_to_response('new_post.html',context_instance=RequestContext(request,
                {'form':form}))
    form = NewPostForm(u)
    return render_to_response('new_post.html',context_instance=RequestContext(request,
            {'form':form}))

#Display rich text editor
def post_view(request):
    """
    form.save_m2m() should be called before saving a form with manytomany relationships
    """
    u = request.user
    try:
        p = Person.objects.get(name=u)
    except ObjectDoesNotExist:
        raise Http404
    if request.method == "POST":
        form = NewPostModelForm(u,p,request.POST)
        if request.POST['share_with'] == 'share with selected friends' and not request.POST.get('selected_friends',''):
            error = True
            return render_to_response('new_post.html',context_instance=RequestContext(request,
                    {'form':form,'p':p,'error':error}))
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.date_posted = format_time(datetime.utcnow())
            new_post.timestamp = format_time(
                format_time(datetime.utcnow()+timedelta(
                    hours = get_timezone_offset(u)[0],
                    minutes = get_timezone_offset(u)[1]
                ))
            )
            new_post.posted_by = u
            new_post.save()
            form.save_m2m()
            if new_post.share_with == 'share with none':
                return HttpResponseRedirect('/drafts-list/')
            else:
                return HttpResponseRedirect('/home/')
        else:
            return render_to_response('new_post.html',context_instance=RequestContext(request,
                    {'form':form,'p':p}))
    form = NewPostModelForm(u,p)
    return render_to_response('new_post.html',context_instance=RequestContext(request,
            {'form':form,'p':p}))


@login_required
def home_content(request):
    u = request.user
    query_str = request.get_full_path()
    user_specialities = u.get_profile().speciality.split(',')
    users = [u]
    user_posts = []
    p = Person.objects.get(name=u.username)
    persons = p.friends.all()
    if persons:
        for member in persons:
            users.append(User.objects.get(username=member))
    for user in users:
        for post in user.userposts_set.exclude(share_with='share with none').exclude(share_with='share with selected friends'):
            if not post.is_spam(u):
                if post.share_with == 'share with related friends' and not post.posted_by == u:
                    for usp in user_specialities:
                        for psp in post.relevance.all():
                            if str(usp) == str(psp):
                                post.can_be_commented = post.comments_allowed(u)
                                post.comments_list = post.comments_set.all()
                                post.num_comments = len(post.comments_list)
                                user_posts.append(post)
                                break
                else:
                    post.can_be_commented = post.comments_allowed(u)
                    post.comments_list = post.comments_set.all()
                    post.num_comments = len(post.comments_list)
                    user_posts.append(post)
        if user.userposts_set.filter(share_with='share with selected friends'):
            for post in user.userposts_set.filter(share_with='share with selected friends'):
                if not post.is_spam(u):
                    friends_list = []
                    for person in post.selected_friends.all():
                        friends_list.append(person.get_user())
                    if u in friends_list or post.posted_by == u:
                        post.can_be_commented = post.comments_allowed(u)
                        post.comments_list = post.comments_set.all()
                        post.num_comments = len(post.comments_list)
                        user_posts.append(post)

        #append status updates to user_posts list
        for status in user.statusupdates_set.all():
            if not status.is_spam(u):
                if status.share_with == 'share with related friends':
                    for usp in user_specialities:
                        for sp in status.posted_by.get_profile().speciality.split(','):
                            if str(usp) == str(sp):
                                status.can_be_commented = status.comments_allowed(u)
                                status.statuscomments_list = status.statuscomments_set.all()
                                commented_by = []
                                if status.statuscomments_set.all():
                                    for item in status.statuscomments_set.all():
                                        if item.posted_by.first_name not in commented_by:
                                            commented_by.append(item.posted_by.first_name)
                                commented_by = ['Dr %s'%i.capitalize() for i in commented_by]
                                status.commented_by = commented_by
                                status.num_comments = len(status.statuscomments_list)
                                user_posts.append(status)
                                break
                else:
                    status.can_be_commented = status.comments_allowed(u)
                    status.statuscomments_list = status.statuscomments_set.all()
                    commented_by = []
                    if status.statuscomments_set.all():
                        for item in status.statuscomments_set.all():
                            if item.posted_by.first_name not in commented_by:
                                commented_by.append(item.posted_by.first_name)
                    commented_by = ['Dr %s'%i.capitalize() for i in commented_by]
                    status.commented_by = commented_by
                    status.num_comments = len(status.statuscomments_list)
                    user_posts.append(status)
    #add posts the user has subscribed to
    subscriptions = u.subscriptions_set.all()
    if subscriptions:
        subscription_user_list = []
        for s in subscriptions:
            subscription_user_list.append(s.subscribed_to)
        for user in subscription_user_list:
            subscribed_posts = user.userposts_set.filter(share_with = 'share with all')
            if subscribed_posts:
                for post in subscribed_posts:
                    if not post.is_spam(u):
                        post.can_be_commented = post.comments_allowed(u)
                        post.comments_list = post.comments_set.all()
                        post.num_comments = len(post.comments_list)
                        user_posts.append(post)
            subscribed_status_posts = user.statusupdates_set.filter(share_with = 'share with all')
            if subscribed_status_posts:
                for status in subscribed_status_posts:
                    if not status.is_spam(u):
                        status.can_be_commented = status.comments_allowed(u)
                        status.statuscomments_list = status.statuscomments_set.all()
                        status.num_comments = len(status.statuscomments_list)
                        user_posts.append(status)
    #sort results by most recent
    sort_key = lambda x: x.date_posted
    user_posts.sort(key=sort_key,reverse=True)
    #paginate results
    post_list = Paginator(user_posts,2)
    try:
        page = int(request.GET.get('page','1'))
    except  ValueError:
        page = 1
    try:
        user_posts = post_list.page(page)
    except (InvalidPage,EmptyPage):
        user_posts = post_list.page(post_list.num_pages)
    if request.is_ajax():
        html = render_to_string('home_content_ajax.html',{
            'user_posts':user_posts,'post_list':post_list,'next':query_str},
        context_instance=RequestContext(request))
        response = html
        return HttpResponse(response)
    else:
        return render_to_response('home-content.html',context_instance=RequestContext(request,
            {'user_posts':user_posts,'post_list':post_list,'next':query_str}))

def post_edit(request,id):
    u = request.user
    try:
        person = Person.objects.get(name=request.user)
    except  ObjectDoesNotExist:
        raise Http404
    post = UserPosts.objects.get(id=int(id))
    friends_selected = post.selected_friends.all()
    query_string = request.GET.get('next',None)
    if request.method == "POST":
        form = PostEditForm(post,person,request.POST,instance=post)
        if request.POST['share_with'] == 'share with selected friends' and not request.POST.get('selected_friends',''):
            error = True
            return render_to_response('new_post.html',context_instance=RequestContext(request,
                    {'form':form,'p':person,'error':error}))
        if form.is_valid():
            p = form.save(commit=False)
            p.date_posted = format_time(datetime.utcnow())
            p.timestamp = format_time(
                format_time(datetime.utcnow()+timedelta(
                    hours = get_timezone_offset(u)[0],
                    minutes = get_timezone_offset(u)[1]
                ))
            )
            p.save()
            form.save_m2m()
            if p.share_with == 'share with none':
                return HttpResponseRedirect('/drafts-list/')
            if 'next' in request.GET:
                return redirect(request.GET['next'])
            return HttpResponseRedirect('/home/')
        else:
            return render_to_response('ajax-edit-post.html',context_instance=RequestContext(request,
            {'form':form,'id':id,'query_string':query_string,'p':person}))
    else:
        form = PostEditForm(post,person,instance=post)
        return render_to_response('ajax-edit-post.html',context_instance=RequestContext(request,
                {'form':form,'id':id,'query_string':query_string,'p':person,'friends_selected':friends_selected}))

#delete post
def delete_post(request,post_id,type):
    if type == 'post':
        post = get_object_or_404(UserPosts,pk=post_id)
    else:
        post = get_object_or_404(StatusUpdates,pk=post_id)
    post.delete()
    if 'next' in request.GET:
        return redirect(request.GET['next'])
    return HttpResponseRedirect('/home-ajax/')

#testing ckeditor
def ckeditor_test(request):
    form = CkEditorTest()
    return render_to_response('ckeditor_test.html',context_instance=RequestContext(request,
            {'form':form}))

#show the user all his/her uploads
@login_required
def image_library(request):
    images = []
    image_path_list = [path for path in get_image_files(user=request.user)]
    #get_image_files is imported from ckeditor views -- 'yields' a generator
    #now image_list should be a list of absolute paths to all uploaded files specific to user
    for path in image_path_list:
        images.append(get_media_url(path))
        #get_image_url is imported form ckeditor views -- returns file's media url
    return render_to_response('image_gallery.html',context_instance=RequestContext(request,
            {'images':images}))

def comment(request,post_id,type):
    u = request.user
    if type == 'post_comment':
        post = get_object_or_404(UserPosts,pk=post_id)
    else:
        post = get_object_or_404(StatusUpdates,pk=post_id)
    if request.method == "POST":
        if type == 'post_comment':
            form = CommentForm(request.POST)
        else:
            form = StatusCommentForm(request.POST)
        if form.is_valid():
            comment_obj = form.save(commit=False)
            comment_obj.posted_by = u
            comment_obj.posted_on = post
            comment_obj.date_commented = format_time(datetime.utcnow())
            comment_obj.timestamp = format_time(
                format_time(datetime.utcnow()+timedelta(
                    hours = get_timezone_offset(u)[0],
                    minutes = get_timezone_offset(u)[1]
                ))
            )
            comment_obj.save()
            if type == 'post_comment':
                html = render_to_string('comments/new_comment.html',
                {'comment':comment_obj,'item':post},context_instance=RequestContext(request))
            else:
                html = render_to_string('comments/status_comment.html',
                        {'comment':comment_obj,'item':post},context_instance=RequestContext(request))
        else:
            #the following code is unnecessary,
            #because we just show a script alert if form.is_valid is false
            if type == 'post_comment':
                html = render_to_string("comments/new_comment_form.html",
                    {'form':form,'post':post},context_instance=RequestContext(request))
            else:
                html = render_to_string('comments/status_comment_form.html',
                        {'form':form,'post':post},context_instance=RequestContext(request))
        if type == 'post_comment':
            num_comments = len(post.get_filtered_comments(u))
        else:
            num_comments = len(post.get_filtered_comments(u))
        response = simplejson.dumps({'html':html,'is_valid':form.is_valid(),'num_comments':str(num_comments)})
        return HttpResponse(response,status=200,mimetype='application/json')
    else:
        #we don't do a get request
        return HttpResponse('')

@login_required
def delete_comment(request,comment_id,type):
    u = request.user
    if type == 'post_comment':
        comment = get_object_or_404(Comments,pk=comment_id)
        comment.delete()
        post = comment.posted_on
        num_comments = len(post.get_filtered_comments(u))
    else:
        comment = get_object_or_404(StatusComments,pk=comment_id)
        comment.delete()
        post = comment.posted_on
        num_comments = len(post.get_filtered_comments(u))
    response = simplejson.dumps({'num_comments':str(num_comments)})
    return HttpResponse(response,status=200,mimetype='application/json')

@login_required
def edit_comment(request,comment_id,type):
    u = request.user
    if type == 'post_comment':
        comment = get_object_or_404(Comments,pk=comment_id)
    else:
        comment = get_object_or_404(StatusComments,pk=comment_id)
    if request.method == "POST":
        if type == 'post_comment':
            form = CommentForm(request.POST,instance=comment)
        else:
            form = StatusCommentForm(request.POST,instance=comment)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.date_commented = format_time(datetime.utcnow())
            obj.timestamp = format_time(
                format_time(datetime.utcnow()+timedelta(
                    hours = get_timezone_offset(u)[0],
                    minutes = get_timezone_offset(u)[1]
                ))
            )
            obj.save()
            if type == 'post_comment':
                html = render_to_string('comments/edited_comment.html',{'comment':obj,'item':obj.posted_on},
                    context_instance=RequestContext(request))
            else:
                html = render_to_string('comments/edited_status_comment.html',{'comment':obj,'item':obj.posted_on},
                    context_instance=RequestContext(request))
        else:
            if type == 'post_comment':
                html = render_to_string('comments/comment_edit.html',{'comment':comment,},
                    context_instance=RequestContext(request))
            else:
                html = render_to_string('comments/status_comment_edit.html',{'comment':comment,},
                    context_instance=RequestContext(request))
    else:
        if type == 'post_comment':
            form = CommentForm(instance=comment)
            html = render_to_string('comments/comment_edit.html',{'comment':comment,},
                context_instance=RequestContext(request))
        else:
            form = StatusCommentForm(instance=comment)
            html = render_to_string('comments/status_comment_edit.html',{'comment':comment,},
                context_instance=RequestContext(request))
    response = simplejson.dumps({'html':html,'is_valid':form.is_valid()})
    return HttpResponse(response,status=200,mimetype='application/json')

#update number of comments per post
#unused function -- for now
def num_comments(request,post):
    p = get_object_or_404(UserPosts,pk=post)
    num_comments = len(p.comments_set.all())
    response = simplejson.dumps({'num_comments':num_comments})
    return HttpResponse(response,status=200,mimetype='application/json')

#status updates
def status_update(request):
    u = request.user
    if request.method == "POST":
        status = StatusUpdates(
            status_update = request.POST['status_update'],
            type = 'status_update',
            posted_by = request.user,
            date_posted = format_time(datetime.utcnow()),
            timestamp = format_time(
                format_time(datetime.utcnow()+timedelta(
                    hours = get_timezone_offset(u)[0],
                    minutes = get_timezone_offset(u)[1]
                ))
            ),
            share_with = u.globalsharesettings.share_with
        )
        try:
            status.save()
        except ValidationError:
            return HttpResponseRedirect('/home/')
    if 'next' in request.GET:
        return redirect(request.GET['next'])
    else:
        return HttpResponseRedirect('/home/')

#edit status update
def edit_status(request,post_id):
    post = get_object_or_404(StatusUpdates,pk=post_id)
    if request.method == "POST":
        form = StatusUpdateEditForm(request.POST,instance=post)
        if form.is_valid():
            edited_status = form.save(commit=False)
            edited_status.date_posted = format_time(datetime.utcnow())
            edited_status.timestamp = format_time(
                format_time(datetime.utcnow()+timedelta(
                    hours = get_timezone_offset(u)[0],
                    minutes = get_timezone_offset(u)[1]
                ))
            )
            edited_status.save()
            html = render_to_string('edited_status_update.html',{'item':edited_status},
                context_instance=RequestContext(request))
        else:
            html = render_to_string('status_update_edit_form.html',{'form':form,'item':post},
                context_instance=RequestContext(request))
        response = simplejson.dumps({'html':html,'is_valid':form.is_valid()})
        return HttpResponse(response,status=200,mimetype='application/json')
    else:
        form = StatusUpdateEditForm(instance=post)
        return render_to_response('status_update_edit_form.html',
            context_instance=RequestContext(request,{'form':form,'item':post}))

#drafts aka unshared posts
def drafts_list(request):
    u = request.user
    posts = UserPosts.objects.filter(posted_by = u).filter(share_with = 'share with none')
    #paginate results
    draft_list = Paginator(posts,10)
    try:
        page = int(request.GET.get('page','1'))
    except ValueError:
        page = 1
    try:
        drafts = draft_list.page(page)
    except (InvalidPage,EmptyPage):
        drafts = draft_list.page(draft_list.num_pages)
    return render_to_response('drafts_list.html',context_instance=RequestContext(request,
            {'drafts':draft_list}))

def draft_detail(request,post_id):
    draft = get_object_or_404(UserPosts,pk=post_id)
    draft.num_comments = len(draft.comments_set.all())
    return render_to_response('draft_detail.html',context_instance=RequestContext(request,{'item':draft}))

#move post to drafts
def move_to_drafts(request,post_id):
    post = get_object_or_404(UserPosts,pk=post_id)
    post.share_with = 'share with none'
    post.save()
    if 'next' in request.GET:
        return redirect(request.GET['next'])
    return HttpResponseRedirect('/home/')

#speciality list
@login_required
def speciality_list(request):
    u = request.user
    speciality_list = []
    user_specialities = u.get_profile().speciality.split(',')
    specialities = Speciality.objects.all()
    for x in specialities:
        if x.name not in user_specialities:
            speciality_list.append(x)
    return render_to_response('speciality_list.html',context_instance=RequestContext(request,
            {'speciality_list':speciality_list,'user_categories':user_specialities}))

@login_required
def speciality(request,sp):
    u = request.user
    try:
        s = Speciality.objects.get(name=str(sp))
    except ObjectDoesNotExist:
        raise  Http404
    user_posts = []
    status_updates_set = u.statusupdates_set.filter(share_with='share with all')
    user_posts_query_set = s.userposts_set.filter(share_with = 'share with all')
    for post in user_posts_query_set:
        post.can_be_commented = post.comments_allowed(u)
        post.num_comments = len(post.comments_set.all())
        user_posts.append(post)
    for item in status_updates_set:
        for sp in item.posted_by.get_profile().speciality.split(','):
            if str(sp) == str(s.name):
                item.can_be_commented = item.comments_allowed(u)
                item.num_comments = len(item.statuscomments_set.all())
                user_posts.append(item)
                break
    sort_key = lambda x:x.date_posted
    user_posts.sort(key=sort_key,reverse=True)
    post_list = Paginator(user_posts,2)
    try:
        page = int(request.GET.get('page','1'))
    except  ValueError:
        page = 1
    try:
        user_posts = post_list.page(page)
    except (InvalidPage,EmptyPage):
        user_posts = post_list.page(post_list.num_pages)
    if request.is_ajax():
        html = render_to_string('speciality_ajax.html',{'user_posts':user_posts,'post_list':post_list,'speciality':s})
        response = simplejson.dumps({'html':html})
        return HttpResponse(response,status=200,mimetype='application/json')
    else:
        return render_to_response('speciality.html',context_instance= RequestContext(request,
            {'user_posts':user_posts,'post_list':post_list,'speciality':s}))

def username_availability(request):
    if request.GET.get('q',''):
        query = request.GET.get('q')
        if re.match(r'^\w{6,20}$',query):
            try:
                User.objects.get(username=query)
                response = '"%s" is not available'%query
            except ObjectDoesNotExist:
                response = '<span style="color:green;font-family:Helvetica,serif;"> "%s" is available</span>'%query
        else:
            response = 'use alphanumerics between 6 and 20 characters'
    else:
        response = 'Try a name first'
    return HttpResponse(response)

def post_detail(request,post_id,type):
    u = request.user
    post_type = type
    if post_type == 'post':
        p = get_object_or_404(UserPosts,pk=post_id)
        #need some code to prevent users from accessing post details
        #by typing urls in browser window

        p.can_be_commented = p.comments_allowed(u)
        p.comments_list = p.comments_set.all()
        cp = p.get_checked_post(u)
        if not cp.has_checked:
            cp.has_checked = True
        cp.save()
    else:
        p = get_object_or_404(StatusUpdates,pk=post_id)
        p.can_be_commented = p.comments_allowed(u)
        p.comments_list = p.statuscomments_set.all()
        cp = p.get_checked_status_post(u)
        if not cp.has_checked:
            cp.has_checked = True
        cp.save()
    return render_to_response('post_detail.html',context_instance=RequestContext(request,{'item':p}))

@cache_control(no_store=True,no_cache=True)
@login_required
def notifications(request,url_type):
    url = url_type
    u = request.user
    relevant_comments = []
    older_comments = []
    user_posts = u.userposts_set.exclude(mark_as='news')
    user_status_updates = u.statusupdates_set.all()
    for post in user_posts:
        cp = post.get_checked_post(u)
        if post.has_new_comments(u):
            if cp.has_checked:
                cp.has_checked = False
                cp.save()
            comments = post.get_new_comments(u)
            for comment in comments:
                if not comment.posted_by == u:
                    relevant_comments.append(comment)
        if not post.has_new_comments(u) and post.comments_set.all():
            if not cp.has_checked:
                for comment in post.comments_set.filter(
                    date_commented__lt = u.get_profile().checked_notifications_on).exclude(posted_by=u):
                    older_comments.append(comment)
    for post in user_status_updates:
        cp = post.get_checked_status_post(u)
        if post.has_new_comments(u):
            if cp.has_checked:
                cp.has_checked = False
                cp.save()
            comments = post.get_new_comments(u)
            for comment in comments:
                if not comment.posted_by == u:
                    relevant_comments.append(comment)
        if not post.has_new_comments(u) and post.statuscomments_set.all():
            if not cp.has_checked:
                for comment in post.statuscomments_set.filter(
                    date_commented__lt = u.get_profile().checked_notifications_on).exclude(posted_by=u):
                    older_comments.append(comment)
    older_comments.sort(key=lambda x:x.date_commented,reverse=True)
    relevant_comments.sort(key=lambda x:x.date_commented,reverse=True)
    person = Person.objects.get(name=u.username)
    friends_query_set = person.friends.all()
    friends = []
    relevant_posts = []
    newly_commented_posts = []
    older_posts = []
    my_specialities = u.get_profile().speciality.split(',')
    for friend in friends_query_set:
        #user is not included in friends list
        friends.append(friend.get_user())
    for user in friends:
        user_speciality = user.get_profile().speciality.split(',')
        posts_query_set_all = user.userposts_set.exclude(share_with='share with none').exclude(
            share_with='share with selected friends').exclude(mark_as = 'news')
        posts_query_set_selected = user.userposts_set.filter(share_with = 'share with selected friends').exclude(mark_as = 'news')
        status_updates_query_set = user.statusupdates_set.all()
        for post in posts_query_set_all:
            if post.share_with == 'share with related friends':
                for relevance in post.relevance.all():
                    if relevance in user_speciality:
                        if post.is_new(u):
                            relevant_posts.append(post)
                        if not post.is_new(u) and post.has_new_comments(u):
                            comments = post.get_new_comments(u)
                            post.new_comments = comments
                            post.num_new_comments = len(comments)
                            cp = post.get_checked_post(u)
                            if cp.has_checked:
                                cp.has_checked = False
                                cp.save()
                            newly_commented_posts.append(post)
                        if not post.is_new(u) and not post.has_new_comments(u):
                            cp = post.get_checked_post(u)
                            if not cp.has_checked:
                                post.num_comments = len(post.comments_set.all())
                                older_posts.append(post)
            else:
                if post.is_new(u):
                    relevant_posts.append(post)
                if not post.is_new(u) and post.has_new_comments(u):
                    comments = post.get_new_comments(u)
                    post.new_comments = comments
                    post.num_new_comments = len(comments)
                    cp = post.get_checked_post(u)
                    if cp.has_checked:
                        cp.has_checked = False
                        cp.save()
                    newly_commented_posts.append(post)
                if not post.is_new(u) and not post.has_new_comments(u):
                    cp = post.get_checked_post(u)
                    if not cp.has_checked:
                        post.num_comments = len(post.comments_set.all())
                        older_posts.append(post)
        for post in posts_query_set_selected:
            selected_friends = post.selected_friends.all()
            if u in selected_friends:
                if post.is_new(u):
                    relevant_posts.append(post)
                if not post.is_new(u) and post.has_new_comments(u):
                    comments = post.get_new_comments(u)
                    post.new_comments = comments
                    post.num_new_comments = len(comments)
                    cp = post.get_checked_post(u)
                    if cp.has_checked:
                        cp.has_checked = False
                        cp.save()
                    newly_commented_posts.append(post)
                if not post.is_new(u) and not post.has_new_comments(u):
                    cp = post.get_checked_post(u)
                    if not cp.has_checked:
                        post.num_comments = len(post.comments_set.all())
                        older_posts.append(post)
        for post in status_updates_query_set:
            if post.share_with == 'share with related friends':
                for speciality in user_speciality:
                    if speciality in my_specialities:
                        if post.is_new(u):
                            relevant_posts.append(post)
                        if not post.is_new(u) and post.has_new_comments(u):
                            comments = post.get_new_comments(u)
                            post.new_comments = comments
                            post.num_new_comments = len(comments)
                            cp = post.get_checked_status_post(u)
                            if cp.has_checked:
                                cp.has_checked = False
                                cp.save()
                            newly_commented_posts.append(post)
                        if not post.is_new(u) and not post.has_new_comments(u):
                            cp = post.get_checked_status_post(u)
                            if not cp.has_checked:
                                post.num_comments = len(post.statuscomments_set.all())
                                older_posts.append(post)
            else:
                if post.is_new(u):
                    relevant_posts.append(post)
                if not post.is_new(u) and post.has_new_comments(u):
                    comments = post.get_new_comments(u)
                    post.new_comments = comments
                    post.num_new_comments = len(comments)
                    cp = post.get_checked_status_post(u)
                    if cp.has_checked:
                        cp.has_checked = False
                        cp.save()
                    newly_commented_posts.append(post)
                if not post.is_new(u) and not post.has_new_comments(u):
                    cp = post.get_checked_status_post(u)
                    if not cp.has_checked:
                        post.num_comments = len(post.statuscomments_set.all())
                        older_posts.append(post)
    relevant_posts.sort(key=lambda x:x.date_posted,reverse=True)
    newly_commented_posts.sort(key=lambda x:x.date_posted,reverse=True)
    older_posts.sort(key=lambda x:x.date_posted,reverse=True)
    if url == 'notifications':
        #change the time when user checked notifications
        up = UserProfile.objects.get(user=u)
        up.checked_notifications_on = format_time(datetime.utcnow())
        up.save()
        if request.is_ajax():
            html = render_to_string('notifications.html',
                    {'relevant_posts':relevant_posts,'older_posts':older_posts,'relevant_comments':relevant_comments,
                     'newly_commented_posts':newly_commented_posts,
                     'older_comments':older_comments},
                context_instance=RequestContext(request))
            response = simplejson.dumps({'html':html})
            return HttpResponse(response,status=200,mimetype='application/json')
        else:
            return render_to_response('notifications.html',context_instance=RequestContext(request,
                    {'relevant_posts':relevant_posts,
                     'older_posts':older_posts,
                     'relevant_comments':relevant_comments,
                     'newly_commented_posts':newly_commented_posts,
                     'older_comments':older_comments}))
    if url == 'alerts':
        num_relevant_posts = len(relevant_posts) + len(newly_commented_posts) + len(relevant_comments)
        response = simplejson.dumps({'post_notifications':num_relevant_posts})
        return HttpResponse(response,status=200,mimetype='application/json')

@cache_control(no_store=True,no_cache=True)
@login_required
def news(request,url_type):
    url = url_type
    u = request.user
    relevant_comments = []
    older_comments = []
    user_posts = u.userposts_set.filter(mark_as='news')
    for post in user_posts:
        cp = post.get_checked_post(u)
        if post.has_new_comments(u):
            if cp.has_checked:
                cp.has_checked = False
                cp.save()
            comments = post.get_new_comments(u)
            for comment in comments:
                if not comment.posted_by == u:
                    relevant_comments.append(comment)
        if not post.has_new_comments(u) and post.comments_set.all():
            if not cp.has_checked:
                for comment in post.comments_set.filter(
                    date_commented__lt = u.get_profile().checked_notifications_on).exclude(posted_by=u):
                    older_comments.append(comment)
    older_comments.sort(key=lambda x:x.date_commented,reverse=True)
    relevant_comments.sort(key=lambda x:x.date_commented,reverse=True)
    person = Person.objects.get(name=u.username)
    friends_query_set = person.friends.all()
    friends = []
    relevant_posts = []
    newly_commented_posts = []
    older_posts = []
    my_specialities = u.get_profile().speciality.split(',')
    for friend in friends_query_set:
        #user is not included in friends list
        friends.append(friend.get_user())
    for user in friends:
        user_speciality = user.get_profile().speciality.split(',')
        posts_query_set_all = user.userposts_set.filter(mark_as='news').exclude(share_with='share with none').exclude(
            share_with='share with selected friends')
        posts_query_set_selected = user.userposts_set.filter(share_with = 'share with selected friends').filter(mark_as = 'news')
        for post in posts_query_set_all:
            if post.share_with == 'share with related friends':
                for relevance in post.relevance.all():
                    if relevance in user_speciality:
                        if post.is_new(u):
                            relevant_posts.append(post)
                        if not post.is_new(u) and post.has_new_comments(u):
                            comments = post.get_new_comments(u)
                            post.new_comments = comments
                            post.num_new_comments = len(comments)
                            cp = post.get_checked_post(u)
                            if cp.has_checked:
                                cp.has_checked = False
                                cp.save()
                            newly_commented_posts.append(post)
                        if not post.is_new(u) and not post.has_new_comments(u):
                            cp = post.get_checked_post(u)
                            if not cp.has_checked:
                                post.num_comments = len(post.comments_set.all())
                                older_posts.append(post)
            else:
                if post.is_new(u):
                    relevant_posts.append(post)
                if not post.is_new(u) and post.has_new_comments(u):
                    comments = post.get_new_comments(u)
                    post.new_comments = comments
                    post.num_new_comments = len(comments)
                    cp = post.get_checked_post(u)
                    if cp.has_checked:
                        cp.has_checked = False
                        cp.save()
                    newly_commented_posts.append(post)
                if not post.is_new(u) and not post.has_new_comments(u):
                    cp = post.get_checked_post(u)
                    if not cp.has_checked:
                        post.num_comments = len(post.comments_set.all())
                        older_posts.append(post)
        for post in posts_query_set_selected:
            selected_friends = post.selected_friends.all()
            if u in selected_friends:
                if post.is_new(u):
                    relevant_posts.append(post)
                if not post.is_new(u) and post.has_new_comments(u):
                    comments = post.get_new_comments(u)
                    post.new_comments = comments
                    post.num_new_comments = len(comments)
                    cp = post.get_checked_post(u)
                    if cp.has_checked:
                        cp.has_checked = False
                        cp.save()
                    newly_commented_posts.append(post)
                if not post.is_new(u) and not post.has_new_comments(u):
                    cp = post.get_checked_post(u)
                    if not cp.has_checked:
                        post.num_comments = len(post.comments_set.all())
                        older_posts.append(post)
    relevant_posts.sort(key=lambda x:x.date_posted,reverse=True)
    newly_commented_posts.sort(key=lambda x:x.date_posted,reverse=True)
    older_posts.sort(key=lambda x:x.date_posted,reverse=True)
    if url == 'news':
        #change the time when user checked notifications
        up = UserProfile.objects.get(user=u)
        #i think this is wrong,UserProfile should have separate field for news_last_checked
        up.checked_notifications_on = format_time(datetime.utcnow())
        up.save()
        if request.is_ajax():
            html = render_to_string('notifications.html',
                    {'relevant_posts':relevant_posts,'older_posts':older_posts,'relevant_comments':relevant_comments,
                     'newly_commented_posts':newly_commented_posts,
                     'older_comments':older_comments},
                context_instance=RequestContext(request))
            response = simplejson.dumps({'html':html})
            return HttpResponse(response,status=200,mimetype='application/json')
        else:
            return render_to_response('notifications.html',context_instance=RequestContext(request,
                    {'relevant_posts':relevant_posts,
                     'older_posts':older_posts,
                     'relevant_comments':relevant_comments,
                     'newly_commented_posts':newly_commented_posts,
                     'older_comments':older_comments}))
    if url == 'news_alerts':
        num_relevant_posts = len(relevant_posts) + len(newly_commented_posts) + len(relevant_comments)
        response = simplejson.dumps({'post_notifications':num_relevant_posts})
        return HttpResponse(response,status=200,mimetype='application/json')

def spam_post(request,post_id):
    referrer = request.META['HTTP_REFERER']
    host = request.get_host()
    next = referrer.replace('http://'+host,'')
    u = request.user
    p = get_object_or_404(UserPosts,pk=post_id)
    if request.method == 'POST':
        spam = SpamPosts.objects.get_or_create(
            reported_by=u,
            post = p
        )
        spam_obj = spam[0]
        form = SpamPostReportForm(request.POST,instance=spam_obj)
        if form.is_valid():
            form.save()
            #we need to send a mail here,to the admins
            if 'next' in request.GET:
                return redirect(request.GET['next'])
            return HttpResponseRedirect(next)
        else:
            spam_obj.delete()
            form = SpamPostReportForm(request.POST)
            return render_to_response('spam_post_report_form.html',
                context_instance=RequestContext(request,{'form':form,'item':p}))
    else:
        form = SpamPostReportForm()
        return render_to_response('spam_post_report_form.html',
            context_instance=RequestContext(request,{'form':form,'item':p,'is_valid':form.is_valid()}))

def hide_post(request,post_id,type):
    referrer = request.META['HTTP_REFERER']
    host = request.get_host()
    next = referrer.replace('http://'+host,'')
    user = request.user
    if type == 'hide_post':
        post = get_object_or_404(UserPosts,pk=post_id)
        spam,created = SpamPosts.objects.get_or_create(
            reported_by = user,
            post = post
            )
        spam.save()
    else:
        post = get_object_or_404(StatusUpdates,pk=post_id)
        spam,created = SpamStatusPosts.objects.get_or_create(
            reported_by = user,
            post = post
        )
        spam.save()
    if 'next' in request.GET:
        return redirect(request.GET['next'])
    return HttpResponseRedirect(next)

def spam_status_post(request,post_id):
    referrer = request.META['HTTP_REFERER']
    host = request.get_host()
    next = referrer.replace('http://'+host,'')
    u = request.user
    p = get_object_or_404(StatusUpdates,pk=post_id)
    if request.method == 'POST':
        spam,created = SpamStatusPosts.objects.get_or_create(
            reported_by = u,
            post = p
        )
        form = SpamStatusPostReportForm(request.POST,instance=spam)
        if form.is_valid():
            form.save()
            if 'next' in request.GET:
                return redirect(request.GET['next'])
            return HttpResponseRedirect(next)
        else:
            spam.delete()
            form = SpamStatusPostReportForm(request.POST)
            return render_to_response('spam_status_post_report_form.html',
                context_instance=RequestContext(request,{'form':form,'item':p}))
    else:
        form = SpamStatusPostReportForm()
        return render_to_response('spam_status_post_report_form.html',
            context_instance=RequestContext(request,{'form':form,'item':p}))

def hide_comment(request,com_id,type):
    u = request.user
    if type == 'comment':
        comment = get_object_or_404(Comments,pk=com_id)
        spam,created = SpamComments.objects.get_or_create(
            hidden_by = u,
            comment = comment
        )
        post = UserPosts.objects.get(id=comment.posted_on.id)
        num_comments = len(post.get_filtered_comments(u))
    else:
        comment = get_object_or_404(StatusComments,pk=com_id)
        spam,created = SpamStatusComments.objects.get_or_create(
            hidden_by = u,
            comment = comment
        )
        post = StatusUpdates.objects.get(id=comment.posted_by.id)
        num_comments = len(post.get_filtered_comments(u))
    response = simplejson.dumps({'num_comments':str(num_comments),'data':''})
    return HttpResponse(response,status=200,mimetype='application/json')

def subscribe(request,id):
    u = request.user
    member = get_object_or_404(User,pk=int(id))
    person_1 = Person.objects.get(name=u.username)
    person_2 = Person.objects.get(name=member.username)
    if person_2.is_friend(u):
        response = 'Dr %s and you are friends already' % member.get_full_name()
        return HttpResponse(response)
    try:
        Subscriptions.objects.filter(subscribed_by=u).get(subscribed_to=member)
        message = 'You have already subscribed to Dr %s'% member.get_full_name()
    except ObjectDoesNotExist:
        Subscriptions.objects.create(subscribed_by=u,subscribed_to=member)
        message = 'Subscribed'
    return HttpResponse(message)

def unsubscribe(request,id):
    path = request.META['HTTP_REFERER']
    u = request.user
    member = get_object_or_404(User,pk=int(id))
    try:
        s = Subscriptions.objects.filter(subscribed_by = u).get(subscribed_to = member)
        s.delete()
    except ObjectDoesNotExist:
        pass
    return HttpResponseRedirect(path)

def check_friend(request,id):
    u = request.user
    member = get_object_or_404(User,pk=int(id))
    p = Person.objects.get(name=u.username)
    if not p.is_friend(member):
        return  HttpResponse('')
    return HttpResponse('friend')

@login_required
def invitation(request):
    u = request.user
    name = u.get_full_name
    context = Context({'doctor':name,'link':'www.doctorslog.net/sign-up/%s/'%uuid4()})
    subject = 'Invitation to join doctorslog'
    text_message = loader.get_template('invitation.txt').render(context)
    html_message = render_to_string('invitation_message.html',context)
    error = None
    if request.POST:
        if 'recipients' in request.POST and request.POST['recipients']:
            recipients = request.POST['recipients']
            final_recipients = []
            recipients = recipients.split(',')
            final_recipients = remove_repeats(recipients,final_recipients)
            for address in recipients:
                try:
                    User.objects.get(email=address)
                    final_recipients.remove(address)
                except ObjectDoesNotExist:
                    pass
            if final_recipients:
                try:
                    mail = EmailMultiAlternatives(
                        subject,
                        text_message,
                        settings.DEFAULT_FROM_EMAIL,
                        final_recipients
                        )
                    mail.attach_alternative(html_message,'text/html')
                    mail.send()
                except smtplib.SMTPException:
                    error = 'Sorry,something went wrong,did you enter valid email address(s) ?'
                    pass
            else:
                error = 'The email address(s) could be already associated with registered user(s)'
    return render_to_response('invitations.html',context_instance=RequestContext(request,{
        'error':error
    }))


