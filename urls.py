from django.conf.urls.defaults import patterns, include, url
from app.models import Comments, StatusComments, StatusUpdates
from app.views import home_view,sign_up, logout_view,settings_view, password_reset_view, \
    profile_picture,ajax_test, ajax_settings, edit_name, edit_username, edit_email, edit_password, my_page, friends_display,\
    fruit_search, user_search, search_results, friend_request, request_alerts, request_details, request_accept, request_ignore, \
    remove_friend, edit_profile_picture, check, inline_share_settings, privacy_settings, global_share_settings, post_view, \
    home_content, post_edit, ckeditor_test, image_library, comment, delete_comment, edit_comment, num_comments, delete_post, \
    status_update, edit_status, drafts_list, draft_detail, move_to_drafts, speciality_list, speciality, anonymous, \
    username_availability, notifications, post_detail, news, spam_post, hide_post, spam_status_post, hide_comment,\
    edit_medical_school_detail, edit_qualification, edit_speciality, edit_profile_details, subscribe, unsubscribe, profile_posts, \
    check_friend, edit_graduation_year, invitation
from django.views.generic import TemplateView
from mysite import settings
from django.views.generic import DetailView

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
                       (r'^$',home_content),
                       (r'^home/$',home_content),
                       (r'^home-ajax/$',home_content),
                       (r'^sign_up/$',sign_up),
                       (r'^success/$',TemplateView.as_view(template_name='success.html')),
                       (r'^login/$','django.contrib.auth.views.login'),
                       (r'^logout/$',logout_view),
                       (r'^settings/$',settings_view),
                       (r'^password_reset/$',password_reset_view),
                       #(r'^edit/',include('mysite.app.profile_settings.urls'),),
                       (r'^profile_picture/$',profile_picture),
                       (r'^ajax_test/$',ajax_test),
                       (r'^ajax_settings/$',ajax_settings),
                       (r'^edit_name/$',edit_name),
                       (r'^edit_username/$',edit_username),
                       (r'^edit_email/$',edit_email),
                       (r'^edit_password/$',edit_password),
                       (r'^edit_profile_picture/$',edit_profile_picture),
                       (r'^edit-medSchool-detail/$',edit_medical_school_detail),
                       (r'^edit-graduation-year/$',edit_graduation_year),
                       (r'^edit-qualification/$',edit_qualification),
                       (r'^edit-speciality/$',edit_speciality),
                       (r'^edit/',include('mysite.app.profileSettings.urls')),
                       (r'^privacy_settings/$',privacy_settings),
                       (r'^global-share-settings/$',global_share_settings),
                       (r'^friends/$',friends_display),
                       (r'^check-friend/(\d+)',check_friend),
                       (r'^remove-friend/(.*)/$',remove_friend),
                       (r'^new_post/$',post_view),
                       (r'^post-edit/(\d+)/$',post_edit),
                       (r'^edit-status/(\d+)/$',edit_status),
                       (r'^status-post-delete/(\d+)/$',delete_post,{'type':'status'}),
                       (r'^post-delete/(\d+)/$',delete_post,{'type':'post'}),
                       (r'^drafts-list/$',drafts_list),
                       (r'^draft-detail/(\d+)/$',draft_detail),
                       (r'^move-to-drafts/(\d+)/$',move_to_drafts),
                       (r'^status/comment/(\d+)/$',comment,{'type':'status_comment'}),
                       (r'^comment/(\d+)/$',comment,{'type':'post_comment'}),
                       (r'^delete_comment/(\d+)/$',delete_comment,{'type':'post_comment'}),
                       (r'^status/delete-comment/(\d+)/$',delete_comment,{'type':'status_comment'}),
                       (r'^edit-comment/(\d+)/$',edit_comment,{'type':'post_comment'}),
                       (r'^status/edit-comment/(\d+)/$',edit_comment,{'type':'status_comment'}),
                       (r'^comment-detail/(?P<pk>\d+)/$',DetailView.as_view(
                           template_name = 'comments/edited_comment.html',
                           model = Comments,
                           context_object_name = 'comment'
                       )),
                       (r'^status/comment-detail/(?P<pk>\d+)',DetailView.as_view(
                           template_name = 'comments/edited_status_comment.html',
                           model = StatusComments,
                           context_object_name = 'comment'
                       )),
                       (r'^status/post-detail/(?P<pk>\d+)/$',DetailView.as_view(
                           template_name = 'edited_status_update.html',
                           model = StatusUpdates,
                           context_object_name = 'item'
                       )),
                       (r'^num_comments/(\d+)/$',num_comments),
                       (r'^status-updates/$',status_update),
                       (r'^image-gallery/$',image_library),
                       (r'^inline-share-settings/$',inline_share_settings),
                       (r'^tinymce/', include('tinymce.urls')),
                       (r'^ckeditor/',include('ckeditor.urls')),
                       (r'^selectable/',include('selectable.urls')),
                       (r'^user_search/$',user_search),
                       (r'^search_results/$',search_results),
                       (r'^friend-request/(.*)/$',friend_request),
                       (r'^subscribe/(\d+)/$',subscribe),
                       (r'^unsubscribe/(\d+)/$',unsubscribe),
                       (r'^request-alerts/$',request_alerts),
                       (r'^request-details/$',request_details),
                       (r'^request-accept/(.*)/$',request_accept),
                       (r'^request-ignore/(.*)/$',request_ignore),
                       (r'^specialities/$',speciality_list),
                       (r'^speciality/(.*)/$',speciality),
                       (r'^post-alerts/$',notifications,{'url_type':'alerts'}),
                       (r'^notifications/$',notifications,{'url_type':'notifications'}),
                       (r'^news-alerts/$',news,{'url_type':'news_alerts'}),
                       (r'^news/$',news,{'url_type':'news'}),
                       (r'^post-detail/(\d+)/$',post_detail,{'type':'post'}),
                       (r'^status-post-detail/(\d+)',post_detail,{'type':'status_post'}),
                       (r'^fruit_search/$',fruit_search),
                       (r'^check/$',check),
                       (r'^ckeditor-test/$',ckeditor_test),
                       (r'^username-availability/$',username_availability),
                       (r'^report-post/(\d+)/$',spam_post),
                       (r'^report-status-post/(\d+)/$',spam_status_post),
                       (r'^hide-post/(\d+)',hide_post,{'type':'hide_post'}),
                       (r'^hide-status-post/(\d+)/$',hide_post,{'type':'hide_status_post'}),
                       (r'^hide-comment/(\d+)/$',hide_comment,{'type':'comment'}),
                       (r'^status/hide-comment/(\d+)/$',hide_comment,{'type':'status_comment'}),
                       (r'^invite/$',invitation),
                       (r'^user/(.*)/$',anonymous),
                       (r'^(?P<person>\w+)/$',my_page),
                       (r'^(?P<person>.*)/posts/$',profile_posts),
                       )
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^mysite/', include('mysite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),


#urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$','django.views.static.serve',{'document_root':settings.STATIC_ROOT}),
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),)
