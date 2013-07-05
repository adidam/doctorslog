__author__ = 'ananth'

from django.conf.urls.defaults import patterns
from app.views import  edit_profile_details

urlpatterns  = patterns(
    '',
    (r'^PG-college/$',edit_profile_details,
         {'editForm':'PGCollegeEditForm',
          'template_edit':"AjaxSettings/PGCollegeEdit.html",
          'template_edit_form':"AjaxSettings/PGCollegeEditForm.html",
          'param':'post_graduation_medical_institute'}),
    (r'^PG-year/$',edit_profile_details,
         {'editForm':'PGYearEditForm',
          'template_edit':"AjaxSettings/PGYearEdit.html",
          'template_edit_form':"AjaxSettings/PGYearEditForm.html",
          'param':'post_graduation_first_year'}),
    (r'^previous-job/$',edit_profile_details,
         {'editForm':'PreviousJobEditForm',
          'template_edit':"AjaxSettings/previousJobDetailEdit.html",
          'template_edit_form':"AjaxSettings/previousJobDetailEditForm.html",
          'param':'previous_job'}),
    (r'^present-job/$',edit_profile_details,
         {'editForm':'PresentJobEditForm',
          'template_edit':"AjaxSettings/presentJobDetailEdit.html",
          'template_edit_form':"AjaxSettings/presentJobDetailEditForm.html",
          'param':'present_job'}),
    (r'^expertise/$',edit_profile_details,
         {'editForm':'ExpertiseEditForm',
          'template_edit':"AjaxSettings/expertiseDetailEdit.html",
          'template_edit_form':"AjaxSettings/expertiseDetailEditForm.html",
          'param':'expertise'}),
    (r'^other-details/$',edit_profile_details,
        {'editForm':'OtherDetailsEditForm',
         'template_edit':"AjaxSettings/otherDetailsEdit.html",
         'template_edit_form':"AjaxSettings/otherDetailsEditForm.html",
         'param':'other_details'}),
)