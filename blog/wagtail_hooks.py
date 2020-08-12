from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register
)

from .models import BlogDetailPage, BlogPageTag


class BlogDetailPageAdmin(ModelAdmin):
    model = BlogDetailPage
    menu_label = "Posts"
    menu_icon = "edit"
    menu_order = 000
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ("custom_title",)
    search_fields = ("custom_title",)


class BlogPageTagAdmin(ModelAdmin):
    model = BlogPageTag
    menu_label = "Tags"
    menu_icon = "tag"
    menu_order = 100
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ("content_object",)
    search_fields = ("content_object",)


class BlogDetailPageGroup(ModelAdminGroup):
    menu_label = "Blogs"
    menu_icon = "pick"
    menu_order = 500
    items = (BlogDetailPageAdmin, BlogPageTagAdmin)


# modeladmin_register(BlogDetailPageGroup)
