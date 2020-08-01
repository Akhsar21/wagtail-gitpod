from django import template
import six

register = template.Library()

@register.inclusion_tag('blog/comments/disqus.html', takes_context=True)
def show_comments(context):
    blog_page = context['blog_page']
    post = context['post']
    path = post_date_url(post, blog_page)

    raw_url = context['request'].get_raw_uri()
    parse_result = six.moves.urllib.parse.urlparse(raw_url)
    abs_path = six.moves.urllib.parse.urlunparse([
        parse_result.scheme,
        parse_result.netloc,
        path,
        "",
        "",
        ""
    ])

    return {'disqus_url': abs_path,
            'disqus_identifier': post.pk,
            'request': context['request']}