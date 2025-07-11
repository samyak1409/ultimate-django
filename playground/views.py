from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    # return HttpResponse("This is the home page of the playground app.")
    return render(request, template_name="index.html", context={"heading": "Home Page"})
