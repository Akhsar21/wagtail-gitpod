from wagtail.core import blocks as streamfield_blocks
from django import forms
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.shortcuts import render

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from rest_framework.fields import Field
from taggit.models import TaggedItemBase, Tag as TaggitTag
from wagtail.api import APIField
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    StreamFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, Orderable
from wagtail.images.api.fields import ImageRenditionField
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.snippets.models import register_snippet
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock

from wagtailcodeblock.blocks import CodeBlock

from streams import blocks


class ImageSerializedField(Field):  # noqa
    """A custom serializer used in Wagtails v2 API."""

    def to_representation(self, value):
        """Return the image URL, title and dimensions."""
        return {
            "url": value.file.url,
            "title": value.title,
            "width": value.width,
            "height": value.height,
        }


class BlogAuthorsOrderable(Orderable):
    """us to select one or more blog authors from Snippet"""

    page = ParentalKey("BlogDetailPage", related_name="blog_authors")
    author = models.ForeignKey("BlogAuthor", on_delete=models.CASCADE)

    panels = [
        SnippetChooserPanel("author")
    ]

    @property
    def author_name(self):
        return self.author.name

    @property
    def author_website(self):
        return self.author.website

    @property
    def author_image(self):
        return self.author.image

    api_fields = [
        APIField("author_name"),
        APIField("author_website"),
        # This is using a custom django rest framework serializer
        APIField("author_image", serializer=ImageSerializedField()),
        # The below APIField is using a Wagtail-built DRF Serializer that supports
        # custom image rendition sizes
        APIField("image",
                 serializer=ImageRenditionField(
                     'fill-200x250',
                     source="author_image"
                 )
                 ),
    ]


@register_snippet
class BlogAuthor(models.Model):
    """Blog author for snippets."""

    name = models.CharField(max_length=100)
    website = models.URLField(blank=True, null=True)
    image = models.ForeignKey('wagtailimages.Image', related_name='+',
                              on_delete=models.SET_NULL, blank=False, null=True)

    panels = [
        MultiFieldPanel([
            FieldPanel("name"),
            ImageChooserPanel("image")
        ], heading="Name and Image"),
        MultiFieldPanel([
            FieldPanel("website"),
        ], heading="Links"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Author"
        verbose_name_plural = "Authors"


@register_snippet
class BlogCategory(models.Model):
    """Blog category for snippets."""

    name = models.CharField(max_length=255)
    slug = models.SlugField(verbose_name="slug", allow_unicode=True,
                            max_length=255, help_text="A slug to identify posts by this category")

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]


class BlogChildPagesSerializer(Field):  # noqa
    def to_representation(self, child_pages):
        # logic in here
        return_posts = []
        for child in child_pages:
            post_dict = {
                'id': child.id,
                'title': child.title,
                'slug': child.slug,
                'url': child.url,
            }
            return_posts.append(post_dict)
        return return_posts
        # Pythonic comprehensions
        # return [
        #     {
        #         'id': child.id,
        #         'title': child.title,
        #         'slug': child.slug,
        #         'url': child.url,
        #     } for child in child_pages
        # ]


class BlogListingPage(RoutablePageMixin, Page):
    """Listing page lists all the Blog Detail Pages"""

    ajax_template = "blog/blog_listing_page_ajax.html"
    max_count = 1
    subpage_types = ["VideoBlogPage", "blog.ArticleBlogPage"]

    custom_title = models.CharField(max_length=100, blank=False,
                                    null=False, help_text="Overwrites the default title")

    content_panels = Page.content_panels + [
        FieldPanel('custom_title')
    ]

    api_fields = [
        APIField(
            "posts",
            serializer=BlogChildPagesSerializer(
                source='get_child_pages')
        ),
    ]

    @property
    def get_child_pages(self):
        return self.get_children().public().live()
        # return self.get_children().public().live().values("id", "title", "slug")

    def get_context(self, request, *args, **kwargs):
        """Adding custom stuff to our content."""
        context = super().get_context(request, *args, **kwargs)
        all_posts = BlogDetailPage.objects.live().public().order_by('-first_published_at')

        if request.GET.get('tag', None):
            tags = request.GET.get('tag')
            all_posts = all_posts.filter(tags__slug__in=[tags])

        paginator = Paginator(all_posts, 6)

        page = request.GET.get("page")
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        # "posts" will have child pages; you'll need to use .specific in the template
        # in order to access child properties, such as youtube_video_id and subtitle
        context["posts"] = posts
        context['authors'] = BlogAuthor.objects.all()
        return context

    @route(r"^july-2019/$", name="july_2019")
    @route(r"^year/(\d+)/(\d+)/$", name="blogs_by_year")
    def blogs_by_year(self, request, year=None, month=None):
        context = self.get_context(request)
        # Implement your BlogDetailPage filter. Maybe something like this:
        # if year is not None and month is not None:
        #     posts = BlogDetailPage.objects.live().public().filter(year=year, month=month)
        # else:
        #     # No year and no month were set, assume this is july-2019 only posts
        #     posts = BlogDetailPage.objects.live().public().filter(year=2019, month=07)
        # print(year)
        # print(month)
        # context["posts"] = posts

        # Note: The below template (latest_posts.html) will need to be adjusted
        return render(request, "blog/latest_posts.html", context)

    @route(r"^category/(?P<cat_slug>[-\w]*)/$", name="category_view")
    def category_view(self, request, cat_slug):
        """Find blog posts based on a category."""
        context = self.get_context(request)

        try:
            # Look for the blog category by its slug.
            category = BlogCategory.objects.get(slug=cat_slug)
        except Exception:
            # Blog category doesnt exist (ie /blog/category/missing-category/)
            # Redirect to self.url, return a 404.. that's up to you!
            category = None

        if category is None:
            # This is an additional check.
            # If the category is None, do something. Maybe default to a particular category.
            # Or redirect the user to /blog/ ¯\_(ツ)_/¯
            pass

        context["posts"] = BlogDetailPage.objects.live(
        ).public().filter(categories__in=[category])

        # Note: The below template (latest_posts.html) will need to be adjusted
        return render(request, "blog/latest_posts.html", context)

    @route(r'^latest/$', name="latest_posts")
    def latest_blog_posts_only_shows_last_5(self, request, *args, **kwargs):
        context = self.get_context(request, *args, **kwargs)
        context['posts'] = context["posts"][:1]
        # context['categories'] = BlogDetailPage.objects.all()
        return render(request, "blog/latest_posts.html", context)

    def get_sitemap_urls(self, request):
        # Uncomment to have no sitemap for this page
        # return []
        sitemap = super().get_sitemap_urls(request)
        sitemap.append(
            {
                "location": self.full_url + self.reverse_subpage("latest_posts"),
                "lastmod": (self.last_published_at or self.latest_revision_created_at),
                "priority": 0.9,
            }
        )
        return sitemap


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey('BlogDetailPage', related_name='tagged_items',
                                 on_delete=models.CASCADE,)


@register_snippet
class Tag(TaggitTag):
    class Meta:
        proxy = True


class BlogDetailPage(Page):
    """Parental blog detail page."""

    subpage_types = []
    parent_page_types = ['BlogListingPage']

    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    custom_title = models.CharField(max_length=100, blank=False,
                                    null=False, help_text="Overwrites the default title")
    banner_image = models.ForeignKey("wagtailimages.Image", blank=False, null=True,
                                     on_delete=models.SET_NULL, related_name="+")
    categories = ParentalManyToManyField("BlogCategory", blank=True)

    content = StreamField([
        ("heading", streamfield_blocks.TextBlock(
            icon='title',
            min_length=10,
            max_length=100,
            template='wagtailcontentstream/blocks/heading.html'
        )),
        ("document", DocumentChooserBlock()),
        ("embed", EmbedBlock(icon='media')),
        ("table", TableBlock(icon='table')),
        ("code", CodeBlock(icon='code')),
        ("title_and_text", blocks.TitleAndTextBlock()),
        ("image", blocks.CaptionedImageBlock()),
        ("full_richtext", blocks.RichtextBlock()),
        ("paragraph", blocks.SimpleRichtextBlock()),
        ("cards", blocks.CardBlock()),
        ("cta", blocks.CTABlock()),
    ], blank=True, null=True,)

    content_panels = Page.content_panels + [
        FieldPanel("custom_title"),
        StreamFieldPanel("content"),
    ]

    banner_panels = [
        FieldPanel("tags"),
        ImageChooserPanel("banner_image"),
        InlinePanel("blog_authors", label="Author", max_num=1),
        MultiFieldPanel([
            FieldPanel("categories", widget=forms.CheckboxSelectMultiple),
        ], heading="Categories"),
    ]

    api_fields = [
        APIField("blog_authors"),
        APIField("content"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(banner_panels, heading="Banner"),
            ObjectList(Page.promote_panels, heading="Promote"),
            ObjectList(Page.settings_panels, heading="Settings"),
        ]
    )

    def save(self, *args, **kwargs):
        """Create a template fragment key.
        Then delete the key."""
        key = make_template_fragment_key(
            "blog_post_preview",
            [self.id]
        )
        cache.delete(key)
        return super().save(*args, **kwargs)

# First subclassed blog post page


class ArticleBlogPage(BlogDetailPage):
    """A subclassed blog post page for articles"""

    subtitle = models.CharField(max_length=100, blank=True, null=True)
    intro_image = models.ForeignKey("wagtailimages.Image", blank=True, null=True,
                                    on_delete=models.SET_NULL, help_text='Best size for this image will be 1400x400')
    content_panels = Page.content_panels + [
        FieldPanel("custom_title"),
        FieldPanel("subtitle"),
        StreamFieldPanel("content"),
    ]

    banner_panels = [
        FieldPanel("tags"),
        ImageChooserPanel("banner_image"),
        ImageChooserPanel('intro_image'),
        InlinePanel("blog_authors", label="Author", max_num=1),
        MultiFieldPanel([
            FieldPanel("categories", widget=forms.CheckboxSelectMultiple),
        ], heading="Categories"),
    ]

    api_fields = [
        APIField("blog_authors"),
        APIField("content"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(banner_panels, heading="Banner"),
            ObjectList(Page.promote_panels, heading="Promote"),
            ObjectList(Page.settings_panels, heading="Settings"),
        ]
    )

# Second subclassed blog post page


class VideoBlogPage(BlogDetailPage):
    """A subclassed blog post page for articles"""

    youtube_video_id = models.CharField(max_length=30)

    content_panels = Page.content_panels + [
        FieldPanel("custom_title"),
        FieldPanel("youtube_video_id"),
        StreamFieldPanel("content"),
    ]

    banner_panels = [
        FieldPanel("tags"),
        ImageChooserPanel("banner_image"),
        InlinePanel("blog_authors", label="Author", max_num=1),
        MultiFieldPanel([
            FieldPanel("categories", widget=forms.CheckboxSelectMultiple),
        ], heading="Categories"),
    ]

    api_fields = [
        APIField("blog_authors"),
        APIField("content"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(banner_panels, heading="Banner"),
            ObjectList(Page.promote_panels, heading="Promote"),
            ObjectList(Page.settings_panels, heading="Settings"),
        ]
    )
