from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from .models import *

# Create your views here.
def index(request):
    timelapse_list = Timelapse.objects.all()
    return render(request, "controller/index.html", {"timelapse_list": timelapse_list})

def detail(request, timelapse_id):
    timelapse = get_object_or_404(Timelapse, pk=timelapse_id)
    return render(request, "controller/detail.html", {"timelapse": timelapse})

