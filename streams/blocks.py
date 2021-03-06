"""Streamfields live in here"""
from django.templatetags.static import static
from django import forms
from wagtail.core import blocks
from wagtail.core.templatetags.wagtailcore_tags import richtext
from wagtail.images.blocks import ImageChooserBlock


class TitleAndTextBlock(blocks.StructBlock):
    """Title and text and norhing else"""

    title = blocks.CharBlock(required=True, help_text='Add your title')
    text = blocks.TextBlock(required=True, help_text='Add additional text')

    class Meta:
        template = "streams/title_and_text_block.html"
        icon = "edit"
        label = "Title & Text"


class CardBlock(blocks.StructBlock):
    """Cards with image and text and button(S)."""

    title = blocks.CharBlock(required=True, help_text='Add your title')

    cards = blocks.ListBlock(
        blocks.StructBlock([
            ("image", ImageChooserBlock(required=True)),
            ("title", blocks.CharBlock(required=True, max_length=40)),
            ("text", blocks.TextBlock(required=True, max_length=200)),
            ("button_page", blocks.PageChooserBlock(required=False)),
            ("button_url", blocks.URLBlock(required=False,
                                           help_text="If the button page above is selected, that will be used first.")),
        ])
    )

    class Meta:
        template = "streams/cards_block.html"
        icon = "grip"
        label = "Staff Cards"


class RichtextBlock(blocks.RichTextBlock):
    """Richtext with all the features."""

    def get_api_representation(self, value, context=None):
        return richtext(value.source)

    class Meta:
        template = "streams/richtext_block.html"
        icon = "doc-full"
        label = "Full Richtext"


class SimpleRichtextBlock(blocks.RichTextBlock):
    """Richtext without (limited) all the features."""

    def __init__(self, required=True, help_text=None, editor="default", features=None, validators=(), **kwargs):
        super().__init__(**kwargs)
        self.features = ['bold', 'italic', 'link', 'ol', 'ul', 'monospace']

    class Meta:
        template = "streams/richtext_block.html"
        icon = "pilcrow"
        label = "Paragraph"


class CTABlock(blocks.StructBlock):
    """A simple call to action section."""

    title = blocks.CharBlock(required=True, max_length=60)
    text = blocks.RichTextBlock(required=True, features=["bold", "italic"])
    button_page = blocks.PageChooserBlock(required=False)
    button_url = blocks.URLBlock(required=False)
    button_text = blocks.CharBlock(required=True, default="Learn More",
                                   max_length=40)

    class Meta:
        template = "streams/cta_block.html"
        icon = "link"
        label = "Call to Action"


class LinkStruckValue(blocks.StructValue):
    """Additional logic for our urls"""

    def url(self):
        button_page = self.get('button_page')
        button_url = self.get('button_url')
        if button_page:
            return button_page.url
        elif button_url:
            return button_url

        return None

    # def latest_posts(self):
    #     return BlogDetailPage.objects.live()[:3]


class ButtonBlock(blocks.StructBlock):
    """An external or internal URL."""

    button_page = blocks.PageChooserBlock(required=False,
                                          help_text='If selected, this url will be used first')
    button_url = blocks.URLBlock(required=False,
                                 help_text='If added, this url will be used secondarily to the button page')

    # def get_context(self, request, *args, **kwargs):
    #     context = super().get_context(request, *args, **kwargs)
    #     context['latest_posts'] = BlogDetailPage.objects.live().public()[:3]
    #     return context

    class Meta:
        template = "streams/button_block.html"
        icon = "placeholder"
        label = "Single Button"
        value_class = LinkStruckValue


class CaptionedImageBlock(blocks.StructBlock):
    """An image block with a caption, credit, and alignment."""

    image = ImageChooserBlock(help_text='The image to display.',)
    caption = blocks.TextBlock(required=False,
                               help_text='The caption will appear under the image, if entered.')
    credit = blocks.TextBlock(required=False,
                              help_text='The credit will appear under the image, if entered.')
    align = blocks.ChoiceBlock(
        choices=[
            ('left', 'Left'),
            ('right', 'Right'),
            ('center', 'Center'),
            ('full', 'Full Width'),
        ],
        default='left',
        help_text='How to align the image in the body of the page.'
    )

    class Meta:
        icon = 'image'
        template = 'streams/captioned_image.html'
        help_text = 'Select an image and add a caption (optional).'


class MapBlock(blocks.StructBlock):
    marker_title = blocks.CharBlock(max_length=120,
                                    help_text="Marker Title 'This will be updated after you save changes.'")
    marker_description = blocks.RichTextBlock()
    zoom_level = blocks.IntegerBlock(min_value=0, max_value=18,
                                     default='2', required=False)
    location_x = blocks.FloatBlock(default='35.0', required=False)
    location_y = blocks.FloatBlock(default='0.16', required=False)
    marker_x = blocks.FloatBlock(default='51.5', required=False)
    marker_y = blocks.FloatBlock(default='-0.09', required=False)

    @property
    def media(self):
        return forms.Media(
            # js=[static("js/leaflet/leaflet.js")],
            # css={'all': [static("js/leaflet/leaflet.css")]}
            js=["https://unpkg.com/leaflet@1.4.0/dist/leaflet.js"],
            css={'all': ["https://unpkg.com/leaflet@1.4.0/dist/leaflet.css"]}
        )

    class Meta:
        form_template = 'streams/admin_blocks/map.html'
        template = 'streams/map.html'
        icon = "site"
