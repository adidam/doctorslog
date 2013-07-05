
from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

#UserProfile class to extend django User model
class UserProfile(models.Model):
    CHOICES = (('Pediatric Medicine','Pediatric Medicine'),#more choices will be added later
               ('Neonatology','Neonatology'),
               ('Radio-diagnosis','Radio-diagnosis'),
               ('Orthopedics','Orthopedics'),
        )
    speciality = models.CharField(max_length = 100,choices = CHOICES)
    country = models.CharField(max_length=50)
    timezone_offset = models.CharField(max_length=5,null=True,blank=True)
    qualification = models.CharField(max_length=300)
    graduation_medical_institute = models.CharField(max_length=300)
    graduation_first_year = models.IntegerField(max_length=4)
    post_graduation_medical_institute = models.CharField(max_length=300,blank=True)
    post_graduation_first_year = models.IntegerField(max_length=4,null=True,blank=True)
    super_speciality_medical_institute = models.CharField(max_length=300,null=True,blank=True)
    super_speciality_first_year = models.IntegerField(max_length=4,null=True,blank=True)
    previous_job = models.CharField(max_length=500,null=True,blank=True)
    present_job = models.CharField(max_length=500,null=True,blank=True)
    expertise = models.CharField(max_length=500,null=True,blank=True)
    consultation = models.CharField(max_length=1000,null=True,blank=True)
    other_details = models.CharField(max_length=1000,null=True,blank=True)
    date_joined = models.DateField()
    password_update_date = models.DateTimeField()
    checked_notifications_on = models.DateTimeField()
    checked_news_on = models.DateTimeField()
    checked_requests_on = models.DateTimeField()
    user = models.ForeignKey(User,unique=True)

    def __unicode__(self):
        return self.user

    def save(self,*args,**kwargs): #this is a custom save method
        #set the date_joined attribute before calling save()
        self.date_joined = datetime.utcnow()
        #then call the base class' save method
        return super(UserProfile,self).save(*args,**kwargs)

    #a method to get profile picture of a user
    def get_profile_picture(self):
        profile_picture = None
        u = User.objects.get(username=self.user)
        try:
            p = ProfilePicture.objects.get(user=u)
        except ObjectDoesNotExist:
            pass
        else:
            profile_picture = p.photo.url
        return profile_picture

#friends
class Person(models.Model):
    name = models.CharField(max_length=30)
    friends = models.ManyToManyField("self")

    def __unicode__(self):
        return self.name

    #a person object method that accepts a user object as parameter that returns a boolean
    #person objects are just a clone of actual user objects
    def get_user(self):
        try:
            user = User.objects.get(username=self.name)
        except ObjectDoesNotExist:
            return None
        return user

    def is_friend(self,user):
        is_friend = False
        friend_list = self.friends.all()
        for friend in friend_list:
            if str(user.username) == str(friend):
                is_friend = True
                break
        return is_friend

    def friend_request_status(self,user):
        if self.name == user.username:
            return None
        u = User.objects.get(username = self.name)
        try:
            fr = FriendRequests.objects.filter(sent_by = u).get(sent_to = user)
        except ObjectDoesNotExist:
            return None
        return fr.status

    def received_request_status(self,user):
        u = User.objects.get(username=self.name)
        try:
            fr = FriendRequests.objects.filter(sent_to=u).get(sent_by=user)
        except ObjectDoesNotExist:
            return None
        return fr.status

    def is_request_received(self,user):
        if self.received_request_status(user):
            return True
        return False

#friend requests
class FriendRequests(models.Model):
    sent_by = models.ForeignKey(User,related_name='sent_requests')
    sent_to = models.ForeignKey(User,related_name='received_requests')
    status = models.CharField(max_length=10)

    def __unicode__(self):
        return '%s to %s'%(self.sent_by,self.sent_to)

#a model to upload user profile pictures
class ProfilePicture(models.Model):
    photo = models.ImageField(upload_to="photos")
    user = models.ForeignKey(User,unique=True)
    pp_update_date = models.DateTimeField()

class GlobalShareSettings(models.Model):
    share_with = models.CharField(max_length=30,default='share with all')
    user = models.OneToOneField(User)

    def __unicode__(self):
        return '%s %s'%(self.user,self.share_with)


#test for django-selectable
class Fruit(models.Model):
    name = models.CharField(max_length=20)

    def __unicode__(self):
        return self.name

class Speciality(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

class UserPosts(models.Model):
    INLINE_SHARE_CHOICES = (
        ('share with all','all members'),
        ('share with friends','friends'),
        ('share with related friends','friends of similar Speciality'),
        ('share with selected friends','selected friends'),
        ('share with none','none'),
        )
    MARK_AS_CHOICES = (
        ('case study','Case Study'),
        ('article','Article'),
        ('research_paper','Research Paper'),
        ('news','News'),
    )
    title = models.CharField(max_length=500)
    subject = models.CharField(max_length=10000)
    mark_as = models.CharField(max_length=100,choices=MARK_AS_CHOICES,default='case study')
    relevance = models.ManyToManyField(Speciality)
    share_with = models.CharField(max_length=100,choices=INLINE_SHARE_CHOICES)
    selected_friends = models.ManyToManyField(Person,null=True,blank=True)
    posted_by = models.ForeignKey(User)
    cleared_by = models.ManyToManyField(User,related_name='cleared_posts')
    date_posted = models.DateTimeField()
    timestamp = models.DateTimeField(null=True,blank=True)

    def __unicode__(self):
        return self.title

    def comments_allowed(self,user):
        p = Person.objects.get(name = self.posted_by)
        if p.is_friend(user) or self.posted_by == user or self.share_with == 'share with all':
            return True
        return

    def is_new(self,user):
        last_checked = user.get_profile().checked_notifications_on
        if last_checked < self.date_posted:
            return True
        return

    def has_new_comments(self,user):
        has_new_comments = False
        last_checked = user.get_profile().checked_notifications_on
        comments = self.comments_set.all()
        if comments:
            for comment in comments:
                #exclude comments made by user -- we need not show comments made by
                #user as notifications to himself , right?
                if not comment.posted_by == user and last_checked < comment.date_commented:
                    has_new_comments = True
                    break
        return has_new_comments

    def get_new_comments(self,user):
        if self.has_new_comments(user):
            #exclude comments made by user -- we need not show comments made by
            #user as notifications to himself , right?
            new_comments = filter(lambda x:x.is_new(user),self.comments_set.exclude(posted_by=user))
            sort_key = lambda x:x.date_commented
            new_comments.sort(key=sort_key)
            return new_comments
        return

    def get_checked_post(self,user):
        vp =  ViewedUserPost.objects.get_or_create(user=user,post=self)
        return vp[0]

    def is_spam(self,user):
        is_spam = False
        try:
            #a user is supposed to mark a particular post as spam only once
            #so that only one spam post object exists for one user and one particular post
            SpamPosts.objects.get(reported_by=user,post=self)
            is_spam = True
        except ObjectDoesNotExist:
            pass
        return is_spam

    def get_filtered_comments(self,user):
        comments = self.comments_set.all()
        filtered_comments = filter(lambda x:x.is_hidden(user)==False,comments)
        return filtered_comments

    class Meta:
        ordering = ['-date_posted']


#status updates
class StatusUpdates(models.Model):
    SHARE_CHOICES = (
        ('share with all','all members'),
        ('share with friends','friends'),
        ('share with related friends','friends of similar Speciality'),
    )
    status_update = models.CharField(max_length=1000)
    type = models.CharField(max_length=20)
    posted_by = models.ForeignKey(User)
    cleared_by = models.ManyToManyField(User,related_name='cleared_status_posts')
    date_posted = models.DateTimeField()
    #share options,for now are tied to global share settings,
    #should provide the user an option to change per status_update,
    #may be we shall do it latter
    share_with = models.CharField(max_length=100,choices=SHARE_CHOICES)
    timestamp = models.DateTimeField(null=True,blank=True)

    def __unicode__(self):
        return self.status_update

    def comments_allowed(self,user):
        p = Person.objects.get(name = self.posted_by)
        if p.is_friend(user) or self.posted_by == user or self.share_with == 'share with all':
            return True
        return False

    def is_new(self,user):
        last_checked = user.get_profile().checked_notifications_on
        if last_checked < self.date_posted:
            return True
        return False

    def has_new_comments(self,user):
        has_new_comments = False
        last_checked = user.get_profile().checked_notifications_on
        comments = self.statuscomments_set.all()
        if comments:
            for comment in comments:
                if not comment.posted_by == user and last_checked < comment.date_commented:
                    has_new_comments = True
                    break
        return has_new_comments

    def get_new_comments(self,user):
        if self.has_new_comments(user):
            new_comments = filter(lambda x:x.is_new(user),self.statuscomments_set.exclude(posted_by=user))
            sort_key = lambda x:x.date_commented
            new_comments.sort(key=sort_key)
            return new_comments
        return

    def get_checked_status_post(self,user):
        vp = ViewedStatusUpdate.objects.get_or_create(user=user,post=self)
        return vp[0]

    def is_spam(self,user):
        is_spam = False
        try:
            #a user is supposed to mark a particular post as spam only once
            #so that only one spam post object exists for one user and one particular post
            SpamStatusPosts.objects.get(reported_by=user,post=self)
            is_spam = True
        except ObjectDoesNotExist:
            pass
        return is_spam

    def get_filtered_comments(self,user):
        comments = self.statuscomments_set.all()
        filtered_comments = filter(lambda x:x.is_hidden(user)==False,comments)
        return filtered_comments


#a model to keep track of viewed posts
class ViewedPosts(models.Model):
    user = models.ForeignKey(User)
    has_checked = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def __unicode__(self):
        return 'viewed by %s - %s'%(self.user,self.has_checked)

class ViewedUserPost(ViewedPosts):
    post = models.ForeignKey(UserPosts)

class ViewedStatusUpdate(ViewedPosts):
    post = models.ForeignKey(StatusUpdates)


#an abstract base class for Comments,StatusComments
class BaseComments(models.Model):
    comment = models.CharField(max_length=1000)
    posted_by = models.ForeignKey(User)
    date_commented = models.DateTimeField()
    timestamp = models.DateTimeField(null=True,blank=True)

    def is_new(self,user):
        last_checked = user.get_profile().checked_notifications_on
        if last_checked < self.date_commented:
            return True
        return False

    class Meta:
        abstract = True
        ordering = ['date_commented']

#inherits BaseComments
class Comments(BaseComments):
    posted_on = models.ForeignKey(UserPosts)

    def __unicode__(self):
        return self.comment

    def is_hidden(self,user):
        is_spam = False
        try:
            SpamComments.objects.get(hidden_by=user,comment=self)
            is_spam = True
        except ObjectDoesNotExist:
            pass
        return is_spam

#inherits BaseComments
class StatusComments(BaseComments):
    posted_on = models.ForeignKey(StatusUpdates)

    def __unicode__(self):
        return self.comment

    def is_hidden(self,user):
        is_spam = False
        try:
            SpamStatusComments.objects.get(hidden_by=user,comment=self)
            is_spam = True
        except ObjectDoesNotExist:
            pass
        return is_spam


class BaseSpamPosts(models.Model):
    reported_by = models.ForeignKey(User)
    reason = models.TextField(max_length=500,default='none')

    class Meta:
        abstract = True

class SpamPosts(BaseSpamPosts):
    post = models.ForeignKey(UserPosts)

    def __unicode__(self):
        return 'reported by-%s reported on user_post id-%s reason-%s'%(self.reported_by,self.post.id,self.reason)

class SpamStatusPosts(BaseSpamPosts):
    post = models.ForeignKey(StatusUpdates)

    def __unicode__(self):
        return 'reported by-%s reported_on status_update id-%s reason-%s'%(self.reported_by,self.post.id,self.reason)

class SpamComments(models.Model):
    hidden_by = models.ForeignKey(User)
    comment = models.ForeignKey(Comments)

    def __unicode__(self):
        return 'hidden_by-%s hidden comment id-%s'%(self.hidden_by,self.comment_id)


class SpamStatusComments(models.Model):
    hidden_by = models.ForeignKey(User)
    comment = models.ForeignKey(StatusComments)

    def __unicode__(self):
        return 'hidden_by-%s hidden comment id-%s'%(self.hidden_by,self.comment_id)


class Subscriptions(models.Model):
    subscribed_by = models.ForeignKey(User)
    subscribed_to = models.ForeignKey(User,related_name='subscribed_to')

    def __unicode__(self):
        return '%s subscribed to %s'%(self.subscribed_by,self.subscribed_to)










