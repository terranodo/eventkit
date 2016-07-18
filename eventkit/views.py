from django.contrib.auth.decorators import login_required
from .service_manager import create_conf_from_wms
import json
from django.http import HttpResponse
from .tasks import task_create_confs_from_voyager
from .forms import RegisterVoyager
from django.shortcuts import render

@login_required
def register_service(request):
    if request.method == "POST":
        service_url = request.POST.get("service_url")
        service_name = request.POST.get("service_name")
        service_type = request.POST.get("service_type")
        if 'wms' in service_type.lower():
            create_conf_from_wms(service_url, name=service_name)
        return HttpResponse("/layers/", status=202)
    else:
        return HttpResponse(
            json.dumps("This endpoint requires POST."),
            content_type='application/json',
            status=405
        )

@login_required
def import_voyager_cart(request):
    if request.is_ajax() or request.method == "POST":
        form = RegisterVoyager(request.POST, request.FILES)
        if form.is_valid():
            task_create_confs_from_voyager.apply_async(args=(form.cleaned_data['voyager_base_url'],
                                                             request.POST.getlist('voyager_ids')))
            return HttpResponse(status=202)
        else:
            return HttpResponse(status=400)
    else:
        form = RegisterVoyager()
        return render(request, 'eventkit/register_voyager.html', {'form': form})

