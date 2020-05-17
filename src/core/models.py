from django.db import models

# Used for image resizing
from stdimage.models import StdImageField

# To indicate which site a record belongs to
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.urls import reverse
from django.forms import ModelForm
from django.conf import settings
from markdown import markdown
from tinymce import HTMLField
import re
from django.utils.text import slugify

from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()

# For the JSON field
from django.contrib.postgres.fields import JSONField

# To get the geometry fields
from django.contrib.gis.db import models

# To be able to set an UUID
import uuid

# To be able to call just the filename in the file field
# Maybe move to def filename @property?
import os

class Tag(models.Model):
    name = models.CharField(max_length=255)
    description = HTMLField(null=True, blank=True)
    parent_tag = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True,
        limit_choices_to={"hidden": False}, related_name="children"
    )
    hidden = models.BooleanField(db_index=True, default=False, help_text="Mark if tag is superseded/not yet approved/deactivated")
    include_in_glossary = models.BooleanField(db_index=True, default=False)
    belongs_to = models.ForeignKey("Record", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def shortcode(self):
        "Returns abbreviation -- text between parenthesis -- if there is any"
        if "(" in self.name:
            s = self.name
            return s[s.find("(")+1:s.find(")")]
        else:
            return self.name

    class Meta:
        ordering = ["name"]

# By default we really only want to see those records that are both public and not deleted
class PublicActiveRecordManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False, is_public=True)

# This returns those records that are private (a check around ownership needs to take place in the codebase)
# and that are not deleted
class PrivateRecordManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class Record(models.Model):
    name = models.CharField(max_length=255)
    description = HTMLField(null=True, blank=True)
    image = StdImageField(upload_to="records", variations={"thumbnail": (480, 480), "large": (1280, 1024)}, blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    spaces = models.ManyToManyField("ReferenceSpace", blank=True)
    sectors = models.ManyToManyField("Sector", blank=True)

    # We use soft deleted
    is_deleted = models.BooleanField(default=False, db_index=True)

    # Only public records are shown; non-public records are used for instance to manage records 
    # belonging to logged-in users only
    is_public = models.BooleanField(default=True, db_index=True)

    # These relationships are managed through separate tables, but they allow for prefetching to make 
    # the queries run much more efficiently
    child_of = models.ManyToManyField("self", through="RecordRelationship", through_fields=("record_child", "record_parent"), symmetrical=False, related_name="parent_of_child")
    parent_to = models.ManyToManyField("self", through="RecordRelationship", through_fields=("record_parent", "record_child"), symmetrical=False, related_name="child_of_parent")

    # We are going to delete this post-launch
    old_id = models.IntegerField(null=True, blank=True, db_index=True, help_text="Only used for the migration between old and new structure")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("project", args=[self.id])

    def get_methodologies(self):
        self.tags.filter(parent_tag__id=318)

    objects_unfiltered = models.Manager()
    objects_include_private = PrivateRecordManager()
    objects = PublicActiveRecordManager()

class Document(Record):
    file = models.FileField(null=True, blank=True, upload_to="files")

    objects_unfiltered = models.Manager()
    objects_include_private = PrivateRecordManager()
    objects = PublicActiveRecordManager()

    def getFileName(self):
      filename = str(self.file).split("/")[1]
      return filename

class Project(Record):
    contributor_page = HTMLField(null=True, blank=True)
    support_page = HTMLField(null=True, blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    STATUS = (
        ("planned", "Planned"),
        ("ongoing", "Ongoing"),
        ("finished", "Finished"),
        ("cancelled", "Cancelled"),
    )
    status = models.CharField(max_length=20, choices=STATUS, default="ongoing")
    has_subsite = models.BooleanField(default=False)
    slug = models.SlugField(max_length=50, unique=True, blank=True, null=True)
    def get_absolute_url(self):
        return reverse("project", args=[self.id])

    objects_unfiltered = models.Manager()
    objects_include_private = PrivateRecordManager()
    objects = PublicActiveRecordManager()

class PublicProject(Record):
    full_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    url = models.URLField(max_length=255, null=True, blank=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    target_finish_date = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    STATUS = (
        ("planned", "Planned"),
        ("ongoing", "Ongoing"),
        ("finished", "Finished"),
        ("cancelled", "Cancelled"),
    )
    status = models.CharField(max_length=20, choices=STATUS, default="ongoing")
    def get_absolute_url(self):
        return reverse("project", args=[self.id])

    objects_unfiltered = models.Manager()
    objects_include_private = PrivateRecordManager()
    objects = PublicActiveRecordManager()

class News(Record):
    date = models.DateField()
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    objects = models.Manager()
    on_site = CurrentSiteManager()
    slug = models.SlugField(max_length=255)
    class Meta:
        verbose_name_plural = "news"
        ordering = ["-date", "-id"]
    def get_absolute_url(self):
        return reverse("news", args=[self.id])
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    objects_unfiltered = models.Manager()
    objects_include_private = PrivateRecordManager()
    objects = PublicActiveRecordManager()

class Blog(Record):
    date = models.DateField()
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    objects = models.Manager()
    on_site = CurrentSiteManager()
    slug = models.SlugField(max_length=255)
    class Meta:
        ordering = ["-date", "-id"]
    def get_absolute_url(self):
        return reverse("blog", args=[self.id])
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    objects_unfiltered = models.Manager()
    objects_include_private = PrivateRecordManager()
    objects = PublicActiveRecordManager()

class Organization(Record):
    url = models.CharField(max_length=255, null=True, blank=True)
    twitter = models.CharField(max_length=255, null=True, blank=True)
    linkedin = models.CharField(max_length=255, null=True, blank=True)
    researchgate = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    slug = models.SlugField(max_length=255)
    ORG_TYPE = (
        ("academic", "Research Institution"),
        ("universities", "Universities"),
        ("city_government", "City Government"),
        ("regional_government", "Regional Government"),
        ("national_government", "National Government"),
        ("statistical_agency", "Statistical Agency"),
        ("private_sector", "Private Sector"),
        ("publisher", "Publishers"),
        ("journal", "Journal"),
        ("society", "Academic Society"),
        ("ngo", "NGO"),
        ("other", "Other"),
    )
    type = models.CharField(max_length=20, choices=ORG_TYPE)
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    def get_absolute_url(self):
        return reverse("library_journal", args=[self.slug])
    def publications(self):
        # To get all the publications we'll get the LibraryItems that are a child
        # record that are linked to this organization (e.g. journal or publishing house) as a parent
        return LibraryItem.objects.select_related("type").filter(child_list__record_parent=self, child_list__relationship__id=2)

    objects_unfiltered = models.Manager()
    objects_include_private = PrivateRecordManager()
    objects = PublicActiveRecordManager()

# This defines the relationships that may exist between users and records, or between records
# For instance authors, admins, employee, funder
class Relationship(models.Model):
    name = models.CharField(max_length=255)
    label = models.CharField(max_length=255)
    slug = models.SlugField(max_length=20, db_index=True, unique=True, blank=True, null=True, help_text="Should only be set for permissions, and should only be modified by the programming team")
    description = models.TextField(null=True, blank=True)
    is_permission = models.BooleanField(default=False, help_text="Mark if this relationship is about giving people permissions in the system")
    def __str__(self):
        return self.label

# This defines a particular relationship between two records.
# For instance: Record 100 (company AA) has the relationship "Funder" of Record 104 (Project BB)
# It will always be in the form of RECORD_PARENT is RELATIONSHIP of RECORD_CHILD
# Wiley is the publisher of the JIE. Wiley = record_parent; JIE = record_child
# Fulano is the author of Paper A. Fulano = record_parent; Paper A = record_child 
class RecordRelationship(models.Model):
    record_parent = models.ForeignKey(Record, on_delete=models.CASCADE, related_name="parent_list")
    relationship = models.ForeignKey(Relationship, on_delete=models.CASCADE)
    record_child = models.ForeignKey(Record, on_delete=models.CASCADE, related_name="child_list")
    def __str__(self):
        return str(self.record_parent) + ' ' + str(self.relationship.label) + ' ' + str(self.record_child)
    class Meta:
        verbose_name_plural = "relationship manager"
        verbose_name = "relationship manager"

class SocialMedia(models.Model):
    record = models.ForeignKey(Record, on_delete=models.CASCADE)
    PLATFORM = [
        ("instagram", "Instagram"),
        ("facebook", "Facebook"),
        ("twitter", "Twitter"),
        ("linkedin", "LinkedIn"),
    ]
    platform = models.CharField(max_length=20, blank=True, null=True, choices=PLATFORM)
    date = models.DateTimeField(null=True, blank=True)
    published = models.BooleanField(default=False)
    blurb = models.TextField(null=True, blank=True)
    response = models.TextField(null=True, blank=True)

class Event(Record):
    EVENT_TYPE = [
        ("conference", "Conference"),
        ("hackathon", "Hackathon"),
        ("workshop", "Workshop"),
        ("seminar", "Seminar"),
        ("summerschool", "Summer School"),
        ("other", "Other"),
    ]
    type = models.CharField(max_length=20, blank=True, null=True, choices=EVENT_TYPE)
    url = models.URLField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    slug = models.SlugField(max_length=255)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    class Meta:
        ordering = ["-start_date", "-id"]
    def get_absolute_url(self):
        return reverse("event", args=[self.id])
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    objects_unfiltered = models.Manager()
    objects_include_private = PrivateRecordManager()
    objects = PublicActiveRecordManager()

class People(Record):
    firstname = models.CharField(max_length=255, null=True, blank=True)
    lastname = models.CharField(max_length=255, null=True, blank=True)
    affiliation = models.CharField(max_length=255,null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    email_public = models.BooleanField(default=False)
    website = models.CharField(max_length=255, null=True, blank=True)
    twitter = models.CharField(max_length=255, null=True, blank=True)
    google_scholar = models.CharField(max_length=255, null=True, blank=True)
    orcid = models.CharField(max_length=255, null=True, blank=True)
    researchgate = models.CharField(max_length=255, null=True, blank=True)
    linkedin = models.CharField(max_length=255, null=True, blank=True)
    research_interests = models.TextField(null=True, blank=True)
    PEOPLE_STATUS = (
        ("active", "Active"),
        ("retired", "Retired"),
        ("deceased", "Deceased"),
        ("inactive", "Inactive"),
        ("pending", "Pending Review"),
    )
    status = models.CharField(max_length=8, choices=PEOPLE_STATUS, default="active")
    site = models.ManyToManyField(Site)
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse("person", args=[self.id])
    class Meta:
        verbose_name_plural = "people"
        ordering = ["name"]

    objects_unfiltered = models.Manager()
    objects_include_private = PrivateRecordManager()
    objects = PublicActiveRecordManager()

class Webpage(Record):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    slug = models.CharField(db_index=True, max_length=100)
    belongs_to = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, limit_choices_to={"is_internal": True}, related_name="webpages")

    objects_unfiltered = models.Manager()
    objects_include_private = PrivateRecordManager()
    objects = PublicActiveRecordManager()

    def get_absolute_url(self):
        return self.slug
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["site", "slug"], name="site_slug")
        ]
        ordering = ["name"]

class WebpageDesign(models.Model):
    webpage = models.OneToOneField(Record, on_delete=models.CASCADE, primary_key=True)
    HEADER = [
        ("inherit", "No custom header - use the project header"),
        ("full", "Full header with title and subtitle"),
        ("small", "Small header; menu only"),
        ("image", "Image underneath menu"),
    ]
    header = models.CharField(max_length=7, choices=HEADER, default="full")
    header_title = models.CharField(max_length=100, null=True, blank=True)
    header_subtitle = models.CharField(max_length=255, null=True, blank=True)
    header_image = StdImageField(upload_to="header_image", variations={"thumbnail": (480, 480), "large": (1280, 1024), "huge": (2560, 1440)}, blank=True, null=True)
    custom_css = models.TextField(null=True, blank=True)
    def __str__(self):
        return self.webpage.name

class ProjectDesign(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, primary_key=True, related_name="design")
    HEADER = [
        ("full", "Full header with title and subtitle"),
        ("small", "Small header; menu only"),
        ("image", "Image underneath menu"),
    ]
    header = models.CharField(max_length=6, choices=HEADER, default="full")
    logo = models.FileField(null=True, blank=True, upload_to="logos")
    custom_css = models.TextField(null=True, blank=True)
    back_link = models.BooleanField(default=True)
    def __str__(self):
        return self.project.name

class ForumMessage(Record):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    documents = models.ManyToManyField(Document)

    def getReply(self):
        return ForumMessage.objects.filter(parent=self)

    def getLastActivity(self):
        return ForumMessage.objects.filter(parent=self).last()

    def getForumMessageFiles(self):
        return self.documents.all()

    def getContent(self):
        return markdown(self.description)

    def get_absolute_url(self):
        return reverse("forum_topic", args=[self.id])

    objects_unfiltered = models.Manager()
    objects_include_private = PrivateRecordManager()
    objects = PublicActiveRecordManager()

class License(models.Model):
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]

class LibraryItemType(models.Model):
    name = models.CharField(max_length=255)
    icon = models.CharField(max_length=255, null=True, blank=True)
    GROUP = (
        ("academic", "Academic"),
        ("theses", "Theses"),
        ("reports", "Reports"),
        ("multimedia", "Multimedia"),
    )
    group = models.CharField(max_length=20, choices=GROUP, null=True, blank=True)

    def __str__(self):
        return self.name
    class Meta:
        ordering = ["name"]

class LibraryItem(Record):
    LANGUAGES = (
        ("EN", "English"),
        ("ES", "Spanish"),
        ("CH", "Chinese"),
        ("FR", "French"),
        ("GE", "German"),
        ("NL", "Dutch"),
        ("OT", "Other"),
    )
    language = models.CharField(max_length=2, choices=LANGUAGES, default="EN")
    title_original_language = models.CharField(max_length=255, blank=True, null=True)
    author_list = models.TextField(null=True, blank=True)
    author_citation = models.TextField(null=True, blank=True)
    bibtex_citation = models.TextField(null=True, blank=True)
    type = models.ForeignKey(LibraryItemType, on_delete=models.CASCADE)
    is_part_of = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)
    year = models.PositiveSmallIntegerField()
    abstract_original_language = models.TextField(null=True, blank=True)
    date_added = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    file = models.FileField(null=True, blank=True, upload_to="library")
    url = models.CharField(max_length=500, null=True, blank=True)
    file_url = models.URLField(null=True, blank=True)
    open_access = models.NullBooleanField(null=True, blank=True)
    doi = models.CharField(max_length=255, null=True, blank=True)
    isbn = models.CharField(max_length=255, null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    license = models.ForeignKey(License, on_delete=models.CASCADE, null=True, blank=True)
    STATUS = (
        ("pending", "Pending"),
        ("active", "Active"),
        ("deleted", "Deleted"),
    )
    # We will delete this after we inserted appropriate work tickets
    status = models.CharField(max_length=8, choices=STATUS, db_index=True, null=True, blank=True, help_text="Old field, do not use")
    #processes = models.ManyToManyField("staf.Process", blank=True, limit_choices_to={"slug__isnull": False})
    #materials = models.ManyToManyField("staf.Material", blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-year", "name"]

    def get_absolute_url(self):
        return reverse("library_item", args=[self.id])

    def authors(self):
        return People.objects.filter(parent_list__record_child=self, parent_list__relationship__id=4)

    def publisher(self):
        list = Organization.objects.filter(parent_list__record_child=self, parent_list__relationship__id=2)
        return list[0] if list else None

    def producer(self):
        list = Organization.objects.filter(parent_list__record_child=self, parent_list__relationship__id=3)
        return list[0] if list else None

    objects_unfiltered = models.Manager()
    objects_include_private = PrivateRecordManager()
    objects = PublicActiveRecordManager()

class Video(LibraryItem):
    embed_code = models.CharField(max_length=20, null=True, blank=True)
    date = models.DateField(blank=True, null=True)
    VIDEO_SITES = [
        ("youtube", "Youtube"),
        ("vimeo", "Vimeo"),
        ("other", "Other"),
    ]
    video_site = models.CharField(max_length=14, choices=VIDEO_SITES)

    def embed(self):
        if self.video_site == "youtube":
            return f'<iframe class="video-embed youtube-video" src="https://www.youtube.com/embed/{self.embed_code}" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'
        elif self.video_site == "vimeo":
            return f'<iframe class="video-embed vimeo-video" title="vimeo-player" src="https://player.vimeo.com/video/{self.embed_code}" frameborder="0" allowfullscreen></iframe>'

    objects_unfiltered = models.Manager()
    objects_include_private = PrivateRecordManager()
    objects = PublicActiveRecordManager()

class Photo(LibraryItem):
    position = models.PositiveSmallIntegerField(null=True, blank=True, db_index=True)
    objects_unfiltered = models.Manager()
    objects_include_private = PrivateRecordManager()
    objects = PublicActiveRecordManager()

class ActivatedSpace(models.Model):
    space = models.ForeignKey("ReferenceSpace", on_delete=models.CASCADE)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    slug = models.CharField(max_length=255, db_index=True)
    def __str__(self):
        return self.space.name
    def get_absolute_url(self):
        return reverse("datahub_dashboard", args=[self.slug])
    def save(self, *args, **kwargs):
        self.slug = slugify(self.space.name)
        super().save(*args, **kwargs)
    class Meta:
        unique_together = ["slug", "site"]

#MOOC's
#class MOOC(models.Model):
#    name = models.CharField(max_length=255)
#    description = models.TextField(null=True, blank=True)
#    date_created = models.DateTimeField(auto_now_add=True)
#
#    def __str__(self):
#        return self.name
#
#class MOOCQuestion(models.Model):
#    question = models.CharField(max_length=255)
#    date_created = models.DateTimeField(auto_now_add=True)
#
#    def __str__(self):
#        return self.question
#
#class MOOCModule(models.Model):
#    mooc = models.ForeignKey(MOOC, on_delete=models.CASCADE, related_name="modules")
#    name = models.CharField(max_length=255)
#    instructions = models.TextField(null=True, blank=True)
#    date_created = models.DateTimeField(auto_now_add=True)
#
#    def __str__(self):
#        return self.name
#
#class MOOCModuleQuestion(models.Model):
#    module = models.ForeignKey(MOOCModule, on_delete=models.CASCADE, related_name="questions")
#    question = models.ForeignKey(MOOCQuestion, on_delete=models.CASCADE)
#    position = models.PositiveSmallIntegerField(db_index=True, null=True, blank=True)
#    date_created = models.DateTimeField(auto_now_add=True)
#
#    def __str__(self):
#        return self.module.name + " - " + self.question.question
#
#    class Meta:
#        ordering = ["position"]
#
#class MOOCVideo(models.Model):
#    video = models.ForeignKey(Video, on_delete=models.CASCADE)
#    module = models.ForeignKey(MOOCModule, on_delete=models.CASCADE)
#    date_created = models.DateTimeField(auto_now_add=True)
#
#    def __str__(self):
#        return self.module.name + " - " + self.video.video_site + " - " + self.video.url
#
#class MOOCAnswer(models.Model):
#    question = models.ForeignKey(MOOCQuestion, on_delete=models.CASCADE)
#    answer = models.CharField(max_length=255)
#    date_created = models.DateTimeField(auto_now_add=True)
#
#    def __str__(self):
#        return self.answer
#
#class MOOCProgress(models.Model):
#    video = models.ForeignKey(MOOCVideo, on_delete=models.CASCADE)
#    module = models.ForeignKey(MOOCModule, on_delete=models.CASCADE)
#    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#    date_created = models.DateTimeField(auto_now_add=True)
#
#    def __str__(self):
#        return self.module.name
#
#class MOOCQuizAnswers(models.Model):
#    mooc = models.ForeignKey(MOOC, on_delete=models.CASCADE)
#    question = models.ForeignKey(MOOCQuestion, on_delete=models.CASCADE)
#    answer = models.ForeignKey(MOOCAnswer, on_delete=models.CASCADE)
#    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#    date_created = models.DateTimeField(auto_now_add=True)
#
#    def __str__(self):
#        return self.mooc.name

class WorkActivity(models.Model):

    class WorkType(models.IntegerChoices):
        CREATE = 1, "Creating"
        UPLOAD = 2, "Uploading"
        REVIEW = 3, "Reviewing"
        CURATE = 4, "Curating"
        SHARE = 5, "Sharing"
        PARTICIPATE = 6, "Participating"
        LEARN = 7, "Learning"
        ADMIN = 8, "Administering"
        PROGRAM = 9, "Programming"
        DESIGN = 10, "Designing"

    type = models.IntegerField(choices=WorkType.choices, db_index=True)
    name = models.CharField(max_length=255)
    instructions = models.TextField(null=True, blank=True)
    default_project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, limit_choices_to={"is_internal": True})
    points = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "work activities"
        ordering = ["name"]

class Work(Record):

    class WorkStatus(models.IntegerChoices):
        OPEN = 1, "Open"
        COMPLETED = 2, "Completed"
        DISCARDED = 3, "Discarded"
        ONHOLD = 4, "On Hold"
        PROGRESS = 5, "In Progress"

    class WorkPriority(models.IntegerChoices):
        LOW = 1, "Low"
        MEDIUM = 2, "Medium"
        HIGH = 3, "High"

    status = models.IntegerField(choices=WorkStatus.choices, db_index=True, default=1)
    priority = models.IntegerField(choices=WorkPriority.choices, db_index=True, default=2)
    part_of_project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, limit_choices_to={"is_internal": True}, related_name="work")
    workactivity = models.ForeignKey(WorkActivity, on_delete=models.CASCADE, null=True, blank=True)
    related_to = models.ForeignKey(Record, on_delete=models.CASCADE, null=True, blank=True, related_name="my_work")
    assigned_to = models.ForeignKey(People, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name if self.name else self.workactivity.name

    class Meta:
        verbose_name_plural = "work items"

class Badge(models.Model):

    class BadgeType(models.IntegerChoices):
        BRONZE = 1, "Bronze"
        SILVER = 2, "Silver"
        GOLD = 3, "Gold"

    type = models.IntegerField(choices=BadgeType.choices, db_index=True)
    code = models.CharField(max_length=20, null=True, blank=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    projects = models.ManyToManyField(Project, blank=True, limit_choices_to={"is_internal": True})
    worktype = models.ManyToManyField(WorkActivity, blank=True) 
    required_quantity = models.PositiveSmallIntegerField(null=True, blank=True)
   
    def __str__(self):
        return self.name

    class Meta:
        ordering = ["code", "type"]

#
#
#
# STAFDB TABLES
#
#
#

# The geocode scheme defines a particular standard, for instance 3166-1 or the South African postal code system
class GeocodeScheme(Record):
    url = models.URLField(null=True, blank=True)
    coverage = models.ForeignKey("ReferenceSpace", on_delete=models.SET_NULL, null=True, blank=True)
    is_comprehensive = models.BooleanField(default=True, db_index=True)
    icon = models.CharField(max_length=50, null=True, blank=True) # Web field

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("stafcp_geocode", args=[self.id])

    class Meta:
        db_table = "stafdb_geocode_scheme"

# Lists all the different levels within the system. Could be a single level (e.g. Postal Code), but it 
# could also include various levels, e.g.: Country > Province > City
# Depth should start at 0 and go up from there
class Geocode(Record):
    scheme = models.ForeignKey(GeocodeScheme, on_delete=models.CASCADE, related_name="geocodes")
    depth = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = "stafdb_geocode"
        ordering = ["depth", "pk"]

# The reference space, for instance the country "South Africa", the city "Cape Town", or the postal code 8000
class ReferenceSpace(Record):
    slug = models.CharField(max_length=255, null=True)
    location = models.ForeignKey("ReferenceSpaceLocation", on_delete=models.SET_NULL, null=True, blank=True)
    geocodes = models.ManyToManyField(Geocode, through="ReferenceSpaceGeocode")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def is_city(self):
        #check = self.geocodes.filter(id=123)
        check = self.geocodes.filter(name="Urban")
        return True if check else False

    @property
    def is_island(self):
        #check = self.geocodes.filter(id=123)
        check = self.geocodes.filter(name="Island")
        return True if check else False

    def photo(self):
        from core.models import Photo
        photo = Photo.objects.filter(space=self, is_deleted=False).order_by("position")
        if photo:
            return photo[0]

    class Meta:
        db_table = "stafdb_referencespace"

class ReferenceSpaceLocation(models.Model):
    space = models.ForeignKey(ReferenceSpace, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    start = models.DateField(null=True, blank=True, db_index=True)
    end = models.DateField(null=True, blank=True, db_index=True)
    geometry = models.GeometryField()
    is_deleted = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return "Location for " + self.space.name

    class Meta:
        db_table = "stafdb_referencespace_location"
        ordering = ["-start"]

class ReferenceSpaceGeocode(models.Model):
    geocode = models.ForeignKey(Geocode, on_delete=models.CASCADE)
    space = models.ForeignKey(ReferenceSpace, on_delete=models.CASCADE)
    identifier = models.CharField(max_length=255, db_index=True, null=True, blank=True)

    class Meta:
        db_table = "stafdb_referencespace_geocode"

class ActivityCatalog(Record):
    url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "stafdb_activitycatalog"
        verbose_name_plural = "activity catalogs"

class Activity(Record):
    catalog = models.ForeignKey(ActivityCatalog, on_delete=models.CASCADE)
    code = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    is_separator = models.BooleanField()
    def __str__(self):
        if self.code:
            return self.code + " - " + self.name
        else:
            return self.name

    class Meta:
        db_table = "stafdb_activity"
        verbose_name_plural = "activities"

# The Flow Diagram describes a system (e.g. the Water sector) and describes the life-cycle based on 
# the processes that take place within it (e.g. Water collection > Water treatment > Use > Wastewater treatment)
class FlowDiagram(Record):

    def get_absolute_url(self):
        return reverse("stafcp_flowdiagram", args=[self.id])

    def __str__(self):
        return self.name

    class Meta:
        db_table = "stafdb_flowdiagram"

class FlowBlocks(models.Model):
    diagram = models.ForeignKey(FlowDiagram, on_delete=models.CASCADE, related_name="blocks")
    origin = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="blocks_from")
    origin_label = models.CharField(max_length=255, null=True, blank=True)
    destination = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="blocks_to")
    destination_label = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.origin.name + " - " + self.destination.name

    def get_destination(self):
        return self.destination_label if self.destination_label else self.destination.name

    def get_origin(self):
        return self.origin_label if self.origin_label else self.origin.name

    def get_destination_slug(self):
        return slugify(self.destination_label) if self.destination_label else slugify(self.destination.name)

    def get_origin_slug(self):
        return slugify(self.origin_label) if self.origin_label else slugify(self.origin.name)

    class Meta:
        db_table = "stafdb_flowblocks"

class MaterialCatalog(Record):
    url = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "stafdb_materialcatalog"

class Material(Record):
    code = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    catalog = models.ForeignKey(MaterialCatalog, on_delete=models.CASCADE, blank=True, null=True)
    #is_separator = models.BooleanField()

    def __str__(self):
        return self.code + " - " + self.name

    class Meta:
        db_table = "stafdb_material"

class Sector(Record):
    icon = models.CharField(max_length=255, null=True, blank=True)
    photo = models.ForeignKey(Photo, on_delete=models.SET_NULL, null=True, blank=True)
    slug = models.SlugField(max_length=255)
    activities = models.ManyToManyField(Activity, db_table="stafdb_sector_activities")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "stafdb_sector"

    #def spaces(self):
    #    return ReferenceSpaceType.objects.filter(processes__in=self.processes.all())
    #def datasets(self):
    #    return DatasetType.objects.filter(Q(origin_process__in=self.processes.all()) | Q(destination_process__in=self.processes.all()))

class UploadSession(Record):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    part_of_project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    meta_data = JSONField(null=True, blank=True)
    TYPE = (
        ("shapefile", "Shapefile"),
        ("flowdata", "Material flow data"),
        ("stockdata", "Material stock data"),
    )
    type = models.CharField(max_length=20, choices=TYPE)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "stafdb_uploadsession"

def upload_directory(instance, filename):
    # file will be uploaded to MEDIA_ROOT/uuid/<filename>
    directory = "uploads/"
    if instance.session.part_of_project:
        directory += "project-" + str(instance.session.part_of_project.id) + "/"
    directory += instance.session.type + "/" + str(instance.session.uuid) + "/" + filename
    return directory

class UploadFile(models.Model):
    session = models.ForeignKey(UploadSession, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to=upload_directory)

    def __str__(self):
        return self.file.name

    @property
    def filename(self):
        return os.path.basename(self.file.name)

    class Meta:
        db_table = "stafdb_uploadfile"

# Need to remove this (and from stafdb models) when resetting migrations
def shapefile_directory():
    pass
