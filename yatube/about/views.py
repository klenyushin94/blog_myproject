from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'about/aboutauthor.html'


class AboutTechView(TemplateView):
    template_name = 'about/abouttech.html'
