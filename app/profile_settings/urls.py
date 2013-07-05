__author__ = 'ananth'
from django.conf.urls.defaults import*
from app.views import profile_settings_view
from app.forms import*
urlpatterns = patterns('',
                      (r'(?P<param>username)/$',profile_settings_view,{'template_name':'settings/username_edit.html',
                                                                       'edit_form':UserNameChangeForm}),
                      (r'(?P<param>first_name)/$',profile_settings_view,{'template_name':'settings/first_name_edit.html',
                                                             'edit_form':FirstNameChangeForm}),
                      (r'(?P<param>last_name)/$',profile_settings_view,{'template_name':'settings/last_name_edit.html',
                                                                        'edit_form':LastNameChangeForm}),
                      (r'(?P<param>email)/$',profile_settings_view,{'template_name':'settings/email_edit.html',
                                                                    'edit_form':EmailChangeForm}),
                      (r'(?P<param>reg_no)/$',profile_settings_view,{'template_name':'settings/reg_no_edit.html',
                                                                     'edit_form':RegNoChangeForm}),
                      (r'(?P<param>expertise)/$',profile_settings_view,{'template_name':'settings/expertise_edit.html',
                                                                        'edit_form':ExpertiseChangeForm}),
                    )