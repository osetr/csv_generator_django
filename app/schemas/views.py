from django.shortcuts import render, redirect
from django.views.generic import View
from .forms import NewSchemaForm
from django.contrib.auth.mixins import LoginRequiredMixin
import re
from .models import Schema, Processing
from django.http import Http404, JsonResponse
import uuid
from django.views.static import serve
import os
from django.utils import timezone


# user_authenticated serves as a filter of available information on the page
# active_page serves to distinguish active pages and non active in navbar
class AddSchemaView(LoginRequiredMixin, View):
    login_url = "/users/sign_in/"

    def get(self, request):
        form = NewSchemaForm()
        user_authenticated = request.user.is_authenticated

        return render(
            request,
            "new_schema.html",
            context={
                "user_authenticated": user_authenticated,
                "active_page": "add_schema",
                "form": form,
            },
        )

    def post(self, request):
        def columns_to_json(columns):
            # frontend give data in html format(just whole table data_sets)
            # this function serves to extract useful data from it
            columns = re.sub(r"<td><a.*?<\/a><\/td>", "", columns)
            columns = re.findall(r"<td.*?\/td>", columns)
            columns = list(
                map(lambda a: re.search(">(.*?)<", a).group(1), columns)
            )

            result = [
                {
                    "name": columns[i * 3],
                    "type": columns[i * 3 + 1],
                    "order": columns[i * 3 + 2],
                    "additional_parameters": {},
                }
                for i in range(int(len(columns) / 3))
            ]
            
            # if column include additional parametrs
            # front give them as type(par1,par2,...)
            # this piece of code separate type and params
            # if new type will added, just update 
            # column["additional_parameters"], giving new name for param
            # don't forget handle with them in celery task
            for column in result:
                if re.findall(r"Text", column["type"]):
                    column["additional_parameters"].update(
                        {
                            "sentences_amount": re.search(
                                "\((.*?)\)", column["type"]
                            ).group(1)
                        }
                    )
                    column.update({"type": "Text"})
            result.sort(key=lambda i: int(i["order"]))

            return result

        form = NewSchemaForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            separator = form.cleaned_data["separator"]
            columns = form.cleaned_data["columns"]
            columns = columns_to_json(columns)
            schema = Schema(
                name=name,
                separator=separator,
                columns=columns,
                author=request.user,
                date=timezone.now(),
            )
            schema.save()

        return redirect("add_schema_v")


# show all files and create new
class EditSchemaView(LoginRequiredMixin, View):
    login_url = "/users/sign_in/"

    def get(self, request, pk):
        user_authenticated = request.user.is_authenticated
        saved_data_sets = Processing.objects.filter(schema_id=pk)

        return render(
            request,
            "edit_schema.html",
            context={
                "user_authenticated": user_authenticated,
                "pk": pk,
                "saved_data_sets": saved_data_sets,
            },
        )


# create new task for celery
def generate_data_ajax(request, pk, rows):
    if request.is_ajax():
        file_id = uuid.uuid4()
        Processing(
            file_id=file_id,
            schema_id=pk,
            rows=rows,
            date=timezone.now()
        ).save()
        return JsonResponse({"response": "Success", "file_id": str(file_id)})
    else:
        raise Http404


# check if celery complete task
def chech_celery_job_ajax(request, pk):
    if request.is_ajax():
        try:
            process = Processing.objects.get(pk=pk)
        except Processing.DoesNotExist:
            response = "File don't exist"
        else:
            if not process.file_ready:
                response = "File not ready"
            else:
                response = "File ready"
        finally:
            return JsonResponse({"response": response})
    else:
        raise Http404


# download file from media dir
def download_file(request, file_id):
    filepath = "./media/" + str(file_id) + ".csv"
    return serve(
        request,
        os.path.basename(filepath),
        os.path.dirname(filepath)
    )
