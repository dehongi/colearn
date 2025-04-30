from django.shortcuts import render
from django.utils.translation import gettext_lazy as _


def home_view(request):
    """Home page view."""
    return render(request, "website/home.html")


def about_view(request):
    """About page view."""
    return render(request, "website/about.html")


def contact_view(request):
    """Contact page view."""
    return render(request, "website/contact.html")


def terms_view(request):
    """Terms of Service page view."""
    return render(request, "website/terms.html")


def privacy_view(request):
    """Privacy Policy page view."""
    return render(request, "website/privacy.html")


def faq_view(request):
    """FAQ page view."""
    faqs = [
        {
            "question": _("What is CoLearn?"),
            "answer": _(
                "CoLearn is a collaborative online learning platform where experts create courses and learners can contribute to improving the content through suggestions and feedback."
            ),
        },
        {
            "question": _("How does the collaborative learning work?"),
            "answer": _(
                "Learners can suggest improvements to course content, propose new topics, and participate in discussions. Instructors review and approve these suggestions to maintain quality while incorporating community insights."
            ),
        },
        {
            "question": _("How can I become an instructor?"),
            "answer": _(
                'During registration, you can select the "Instructor" role. As an instructor, you can create courses, manage content, and review learner suggestions.'
            ),
        },
        {
            "question": _("Is CoLearn free to use?"),
            "answer": _(
                "CoLearn offers both free and premium courses. The platform itself is free to join, but some courses may require payment."
            ),
        },
        {
            "question": _("How can I suggest improvements to a course?"),
            "answer": _(
                "While viewing course content, you can use the suggestion feature to propose changes, improvements, or additions to the material."
            ),
        },
        {
            "question": _("How are course suggestions reviewed?"),
            "answer": _(
                "Course instructors review all suggestions and can accept, reject, or modify them before incorporating them into the official course material."
            ),
        },
    ]
    return render(request, "website/faq.html", {"faqs": faqs})
