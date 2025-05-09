from django import template
from django.utils.safestring import mark_safe
import markdown
from bleach import clean, ALLOWED_TAGS, ALLOWED_ATTRIBUTES

register = template.Library()

# Create our own set of allowed tags based on bleach's defaults plus our additions
MY_ALLOWED_TAGS = list(ALLOWED_TAGS) + [
    "p",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "pre",
    "code",
    "blockquote",
    "strong",
    "em",
    "ul",
    "ol",
    "li",
    "span",
    "div",
    "img",
    "a",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
    "hr",
    "br",
    "sub",
    "sup",
]

# Create our own dictionary of allowed attributes
MY_ALLOWED_ATTRIBUTES = dict(ALLOWED_ATTRIBUTES)
# Update with our additional attributes
MY_ALLOWED_ATTRIBUTES.update(
    {
        "a": ["href", "title", "target", "rel"],
        "img": ["src", "alt", "title", "width", "height", "class"],
        "code": ["class"],
        "pre": ["class"],
        "span": ["class", "style"],
        "div": ["class", "id"],
        "table": ["class", "border"],
        "th": ["scope", "colspan", "rowspan"],
        "td": ["colspan", "rowspan"],
    }
)


@register.filter(name="markdown_safe")
def markdown_safe(value):
    """Convert markdown text to HTML and sanitize it for safe display"""
    if not value:
        return ""

    # Convert markdown to HTML
    html = markdown.markdown(
        value,
        extensions=[
            "markdown.extensions.fenced_code",
            "markdown.extensions.tables",
            "markdown.extensions.nl2br",
            "markdown.extensions.sane_lists",
        ],
    )

    # Clean HTML to remove unsafe tags
    sanitized_html = clean(
        html, tags=MY_ALLOWED_TAGS, attributes=MY_ALLOWED_ATTRIBUTES, strip=True
    )

    return mark_safe(sanitized_html)
