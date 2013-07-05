from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.forms import ModelForm
import re
from app.lookups import UserLookup
from app.models import ProfilePicture,UserPosts, Comments, StatusComments, StatusUpdates, SpamPosts, SpamStatusPosts
from tinymce.widgets import  TinyMCE
from selectable.forms import widgets
from lookups import FruitLookUp
from ckeditor.widgets import  CKEditorWidget
from countries import countries
from timezones import timezones

pattern = r'\w+\.?|_?'

def validate_name(name):
    if not re.search(r'^\w+$',name):
        raise ValidationError(u'Use alphanumerics and underscore characters only' )


SP_CHOICES = (
    ('Pediatric Medicine','Pediatric Medicine'),
    ('Neonatology','Neonatology'),
    ('Internal Medicine','Internal Medicine'),
    ('Nephrology','Nephrology'),
    ('Radio-diagnosis','Radio-diagnosis'),
    ('Orthopedics','Orthopedics'),
              )

#a form to allow user registration
#could have used ModelForm instead, may be this will be changed latter
class RegistrationForm(forms.Form):

    first_name = forms.CharField(max_length=20)
    last_name = forms.CharField(max_length=20)
    username = forms.CharField(max_length=30,min_length=6)
    email = forms.EmailField()
    Password = forms.CharField(max_length=20,min_length=8,widget=forms.PasswordInput())
    Password2 = forms.CharField(max_length=20,min_length=8,widget=forms.PasswordInput())
    #timezones not yet implemented
    timezone_offset = forms.ChoiceField(choices=timezones.TIME_ZONE_CHOICES,required=False,label='Timezone')
    country = forms.ChoiceField(choices=countries.countries)
    qualification = forms.CharField(max_length=300,widget=forms.Textarea(
        attrs={'rows':2,'cols':30}
    ))
    medical_institute = forms.CharField(max_length=300,widget=forms.Textarea(
        attrs={'rows':1,'cols':30}
    ))
    first_year_of_graduation = forms.IntegerField()
    post_graduation_medical_institute = forms.CharField(max_length=300,widget=forms.Textarea(
        attrs={'rows':1,'cols':30}
    ),label='Post-graduation from',required=False)
    first_year_of_post_graduation = forms.IntegerField(required=False,label='First year of Post-graduation')
    super_speciality_from = forms.CharField(required=False,label='Super speciality/Fellowship from',max_length=300)
    first_year_of_super_speciality = forms.IntegerField(required=False,label='First year of Super speciality/Fellowship')
    speciality = forms.MultipleChoiceField(choices=SP_CHOICES,widget=forms.SelectMultiple())

    def clean_first_name(self):
        is_valid = True
        first_name = self.cleaned_data['first_name']
        first_name = first_name.strip().lower()
        word_list = first_name.split(' ')
        num_words = len(word_list)
        if num_words > 2:
            for word in word_list[1:-1]:
                if re.search(r'\S+',word):
                    is_valid = False
                    break
            if is_valid:
                first_name = word_list[0]+' '+word_list[-1]
                return first_name
            raise forms.ValidationError("First Name & (optional)Middle Name: Enter first name and an optional "
                                        "middle name with a space in between")
        else:
            if re.search(r'^[a-z]+\s{0,1}[a-z]*$',first_name):
                is_valid = True
            else:
                is_valid = False
        if is_valid:
            return first_name
        raise forms.ValidationError(
            "First Name & (optional)Middle Name: only alphabets are allowed")

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        last_name = last_name.strip().lower()
        if re.search(r'^[a-z]{1,20}$',last_name):
            return last_name
        raise  forms.ValidationError('Last name should be alphabets,max of 20')

    def clean_username(self):
        username = self.cleaned_data['username']
        result = re.search('^\w{6,20}$',username)
        if not result:
            raise forms.ValidationError('alphanumerics,"_" only,between 6 and 20 characters,avoid spaces')
        try:
            User.objects.get(username=username)
            raise forms.ValidationError('username already taken,try another one')
        except ObjectDoesNotExist:
            return  username

    #validation on password
    def clean_Password2(self):
        Password = self.cleaned_data['Password']
        Password2 = self.cleaned_data['Password2']
        if Password == Password2:
            return Password
        raise forms.ValidationError('passwords did not match')

    #check if the primary email has been associated with another user
    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            User.objects.get(email=email)
        except  ObjectDoesNotExist:
            return email
        raise forms.ValidationError('This email has been associated with another user')

#forms to edit user profile
#a form to change username
class UserNameChangeForm(forms.Form):
    username = forms.CharField(max_length=20,label='New Username')


#form to change password
class PasswordChangeForm(forms.Form):
    password = forms.CharField(max_length=20,widget=forms.PasswordInput)
    new_password = forms.CharField(max_length=20,min_length=6,widget=forms.PasswordInput)
    new_password_again = forms.CharField(max_length=20,widget=forms.PasswordInput)

#form to change first name
class FirstNameChangeForm(forms.Form):
    first_name = forms.CharField(max_length=30,validators=[validate_name])

#form to change last name
class LastNameChangeForm(forms.Form):
    last_name = forms.CharField(max_length=30,validators=[validate_name])

#email edit form
class EmailChangeForm(forms.Form):
    email = forms.EmailField()

#registration number edit form
class RegNoChangeForm(forms.Form):
    registration_number = forms.IntegerField()

#expertise edit form
class ExpertiseChangeForm(forms.Form):
    expertise = forms.CharField(max_length=300,widget=forms.Textarea())

#form to add profile picture
class ProfilePictureForm(ModelForm):
    class Meta:
        model = ProfilePicture
        fields = ('photo',)

#edit name
class NameChangeForm(forms.Form):
    first_name = forms.CharField(max_length=30,label='First name & Middle name(optional)')
    last_name = forms.CharField(max_length=30)

    def clean_first_name(self):
        is_valid = True
        first_name = self.cleaned_data['first_name']
        first_name = first_name.strip().lower()
        word_list = first_name.split(' ')
        num_words = len(word_list)
        if num_words > 2:
            for word in word_list[1:-1]:
                if re.search(r'\S+',word):
                    is_valid = False
                    break
            if is_valid:
                first_name = word_list[0]+' '+word_list[-1]
                return first_name
            raise forms.ValidationError("First Name & (optional)Middle Name: Enter first name and an optional "
                                        "middle name with a space in between")
        else:
            if re.search(r'^[a-z]+\s{0,1}[a-z]*$',first_name):
                is_valid = True
            else:
                is_valid = False
        if is_valid:
            return first_name
        raise forms.ValidationError(
            "First Name & (optional)Middle Name: only alphabets are allowed")

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        last_name = last_name.lower().strip()
        if re.search(r'^[a-z]+$',last_name):
            return last_name
        raise forms.ValidationError('Last Name: Use only alphabets and a single name')

class MedicalSchoolDetailEditForm(forms.Form):
    medical_school = forms.CharField(max_length=300,
        label='Medical School/University',
        help_text='Press Enter or Return on Mac to produce line breaks',
        widget=forms.Textarea(attrs={'rows':3,'cols':30}))

class GraduationYearEditForm(forms.Form):
    graduation_year = forms.IntegerField()

class PGCollegeEditForm(forms.Form):
    post_graduation_medical_institute = forms.CharField(max_length=300,
        required=False,
        label='Medical School/University',
        help_text='Press Enter or Return on Mac to produce line breaks',
        widget=forms.Textarea(attrs={'rows':3,'cols':30}))

    def clean_medical_school(self):
        medical_school = self.cleaned_data.get('medical_school','')
        if medical_school:
            medical_school = medical_school.strip()
        return medical_school

class PGYearEditForm(forms.Form):
    post_graduation_first_year = forms.IntegerField(required=False,
    label="First year of post-graduation")

    def clean_post_graduation_first_year(self):
        post_graduation_first_year = self.cleaned_data.get('post_graduation_first_year','')
        if post_graduation_first_year:
            post_graduation_first_year = str(post_graduation_first_year).strip()
            if len(post_graduation_first_year) != 4:
                raise  forms.ValidationError('Invalid entry,Year should be in this format - YYYY')
            return int(post_graduation_first_year)
        return post_graduation_first_year

class QualificationEditForm(forms.Form):
    qualification = forms.CharField(max_length=300,
        help_text='Press Enter or Return on Mac to produce line breaks',
        widget=forms.Textarea(attrs={'rows':3,'cols':30})
    )

class SpecialityEditForm(forms.Form):
    speciality = forms.MultipleChoiceField(
        choices=SP_CHOICES,
        widget=forms.SelectMultiple(),
        help_text='Hold down "Ctrl" or "Command" on Mac to select more than one choice'
    )

class PresentJobEditForm(forms.Form):
    present_job =forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={'rows':3,'cols':30}),
        help_text='Press "Enter" or "Return" on Mac to produce line breaks'
    )
    def clean_present_job(self):
        present_job = self.cleaned_data.get('present_job','')
        if present_job:
            present_job = present_job.strip()
        return present_job

class PreviousJobEditForm(forms.Form):
    previous_job =forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={'rows':3,'cols':30}),
        help_text='Press "Enter" or "Return" on Mac to produce line breaks'
    )
    def clean_previous_job(self):
        previous_job = self.cleaned_data.get('previous_job','')
        if previous_job:
            previous_job = previous_job.strip()
        return previous_job

class ExpertiseEditForm(forms.Form):
    expertise =forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={'rows':3,'cols':30}),
        help_text='Press "Enter" or "Return" on Mac to produce line breaks'
    )
    def clean_expertise(self):
        expertise = self.cleaned_data.get('expertise','')
        if expertise:
            expertise = expertise.strip()
        return expertise

class OtherDetailsEditForm(forms.Form):
    other_details =forms.CharField(
        max_length=1000,
        required=False,
        widget=forms.Textarea(attrs={'rows':3,'cols':30}),
        help_text='Press "Enter" or "Return" on Mac to produce line breaks'
    )
    def clean_other_details(self):
        other_details = self.cleaned_data.get('other_details','')
        if other_details:
            other_details = other_details.strip()
        return other_details

class UserSearch(forms.Form):
    name = forms.CharField(
        label="Find friends",
        widget = widgets.AutoCompleteWidget(UserLookup),
        required = False,
    )


#testing tinymce
#class NewPostForm(forms.Form):
 #   title = forms.CharField(max_length=100,widget=forms.Textarea(
  #      attrs = {'rows':3,'cols':75}
   # ))
    #subject = forms.CharField(max_length=500,label='Subject',widget=TinyMCE(attrs={'rows':20,'cols':75}))

class NewPostForm(forms.Form):
    MARK_AS_CHOICES = (

            ('case study','Case Study'),
            ('article','Article'),
            ('research paper','Research Paper'),
            )

    title = forms.CharField(max_length=300,widget=forms.Textarea(attrs={'rows':3,'cols':75}))
    subject = forms.CharField(max_length=1000,widget=TinyMCE(attrs={'rows':20,'cols':75}))
    relevance = forms.MultipleChoiceField(widget=forms.SelectMultiple(),choices=SP_CHOICES)
    mark_as = forms.ChoiceField(choices=MARK_AS_CHOICES,widget=forms.RadioSelect())

    def __init__(self,user,*args,**kwargs):
        super(NewPostForm,self).__init__(*args,**kwargs)
        self.fields['share_with'] = forms.ChoiceField(choices=GlobalShareSettingsForm.CHOICES,
            initial=user.globalsharesettings.share_with,widget=forms.RadioSelect())

INLINE_CHOICES = (
    ('share with all','all members'),
    ('share with friends','friends'),
    ('share with related friends','friends of similar Speciality'),
    ('share with selected friends','selected friends'),
    ('share with none','none'),
    )

class NewPostModelForm(ModelForm):
    class Meta:
        model = UserPosts
        fields = ('title','subject','mark_as','relevance','share_with','selected_friends',)

        widgets = {
            'title':forms.Textarea(attrs={'rows':2,'cols':75}),
            'subject':CKEditorWidget(),
            'mark_as':forms.RadioSelect(),
            'relevance':forms.SelectMultiple(),
            'share_with':forms.RadioSelect(),
            'selected_friends':forms.SelectMultiple(),
        }
    def __init__(self,u,p,*args,**kwargs):
        super(NewPostModelForm,self).__init__(*args,**kwargs)
        self.fields['share_with'] = forms.ChoiceField(choices=INLINE_CHOICES,
        widget=forms.RadioSelect(),initial=u.globalsharesettings.share_with)
        self.fields['selected_friends'] = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(),
            queryset=p.friends.all(),required=False)

class PostEditForm(ModelForm):
    class Meta:
        model = UserPosts

        fields = ('title','subject','mark_as','relevance','share_with','selected_friends',)

        widgets = {
            'title':forms.Textarea(attrs={'rows':2,'cols':60}),
            'subject':CKEditorWidget(),
            'mark_as':forms.RadioSelect(),
            'relevance':forms.SelectMultiple(),
            'share_with':forms.RadioSelect(),
            'selected_friends':forms.SelectMultiple(),
        }
    def __init__(self,post,p,*args,**kwargs):
        super(PostEditForm,self).__init__(*args,**kwargs)
        self.fields['share_with'] = forms.ChoiceField(choices=INLINE_CHOICES,
            widget=forms.RadioSelect(),initial=post.share_with)
        self.fields['selected_friends'] = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(),
            queryset=p.friends.all(),required=False)

#testing django-selectable
class FruitForm(forms.Form):
    autocomplete = forms.CharField(
        label="select the name of fruit",
        widget = widgets.AutoCompleteWidget(FruitLookUp),
        required = False,
    )

class GlobalShareSettingsForm(forms.Form):
    CHOICES = (
        ('share with all','all members'),
        ('share with friends','friends'),
        ('share with related friends','friends of similar Speciality'),
        )
    def __init__(self,user,*args,**kwargs):
        super(GlobalShareSettingsForm,self).__init__(*args,**kwargs)
        self.fields['share_with'] = forms.ChoiceField(choices=self.CHOICES,widget=forms.RadioSelect,
            initial=user.globalsharesettings.share_with,label='Your posts will be shared with')

class InlineShareSettingsForm(GlobalShareSettingsForm):
    def __init__(self,user,*args,**kwargs):
        super(InlineShareSettingsForm,self).__init__(user,*args,**kwargs)
        INLINE_CHOICES = (
            ('share with all','all members'),
            ('share with friends','friends'),
            ('share with related friends','friends of similar Speciality'),
            ('share with none','none'),
            )
        self.fields['share_with'] = forms.ChoiceField(choices=INLINE_CHOICES,widget=forms.RadioSelect,
        initial=user.globalsharesettings.share_with,label='Share this post with')


class CommentForm(ModelForm):
    class Meta:
        model = Comments
        fields = ('comment',)
        widgets = {
            'comment':forms.Textarea(attrs=({'rows':2,'cols':60}))
        }

    def clean_comment(self):
        comment = self.cleaned_data.get('comment')
        if re.search(r'\S+',str(comment)):
            return self.cleaned_data['comment']
        else:
            raise forms.ValidationError("comments cannot be spaces")


#testing ckeditor
class CkEditorTest(forms.Form):
    post = forms.CharField(max_length=1000,widget=CKEditorWidget(attrs={'rows':15,'cols':60}))

class StatusUpdateEditForm(ModelForm):
    class Meta:
        model = StatusUpdates
        fields = ('status_update',)
        widgets = {
            'status_update':forms.Textarea(attrs={'rows':4,'cols':45})
        }

class StatusCommentForm(ModelForm):
    class Meta:
        model = StatusComments
        fields = ('comment',)
        widgets = {
            'comment':forms.Textarea(attrs=({'rows':2,'cols':60}))
        }
    def clean_comment(self):
        comment = self.cleaned_data.get('comment')
        if re.search(r'\S+',str(comment)):
            return self.cleaned_data['comment']
        else:
            raise forms.ValidationError("Enter some text")


class SpamPostReportForm(ModelForm):
    class Meta:
        model = SpamPosts
        fields = ('reason',)
        widgets = {
            'reason':forms.Textarea(attrs=({'rows':2,'cols':60}))
        }

class SpamStatusPostReportForm(ModelForm):
    class Meta:
        model = SpamStatusPosts
        fields = ('reason',)
        widgets = {
            'reason':forms.Textarea(attrs=({'rows':2,'cols':60}))
        }



    
