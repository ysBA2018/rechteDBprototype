import csv
from datetime import datetime

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.views import generic
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView
from rest_framework.response import Response

from .forms import SomeForm, CustomUserCreationForm
from .models import *


class Login(generic.TemplateView):
    template_name = 'myRDB/registration/login.html'


class Logout(generic.TemplateView):
    template_name = 'myRDB/registration/logout.html'


class Register(generic.CreateView):
    template_name = 'myRDB/registration/register.html'
    form_class = CustomUserCreationForm
    success_url = '/myRDB/login'


class Password_Reset(generic.TemplateView):
    template_name = 'myRDB/registration/password_reset_form.html'


class Password_Reset_Done(generic.TemplateView):
    template_name = 'myRDB/registration/password_reset_done.html'


class Password_Reset_Confirm(generic.TemplateView):
    template_name = 'myRDB/registration/password_reset_confirm.html'


class Password_Reset_Complete(generic.TemplateView):
    template_name = 'myRDB/registration/password_reset_complete.html'


class Compare(generic.ListView):
    model = User
    template_name = 'myRDB/compare.html'
    paginate_by = 10
    context_object_name = "table_data"
    extra_context = {}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(self.request.GET['userSearch'])
        compareUserIdentity = self.request.GET['userSearch']
        compareUser = User.objects.filter(identity=compareUserIdentity)
        compUserRoles = Role.objects.filter(user__id=compareUser[0].id)
        compUserAfs = AF.objects.filter(afOwningUser__id=compareUser[0].id)

        data, comp_gf_count, comp_tf_count = User.retrieve_related_rights(User, compareUser[0], compUserRoles,
                                                                          compUserAfs, True)

        compare_paginator = Paginator(list(data), 10)
        page = self.request.GET.get('compare_page')

        try:
            compare_data = compare_paginator.page(page)
        except PageNotAnInteger:
            compare_data = compare_paginator.page(1)
        except EmptyPage:
            compare_data = compare_paginator.page(compare_paginator.num_pages)

        context['comp_role_count'] = compUserRoles.count()
        context['comp_af_count'] = compUserAfs.count()
        context['comp_gf_count'] = comp_gf_count
        context['comp_tf_count'] = comp_tf_count
        context["compareUser"] = compareUser[0]
        context["compareUser_table_data"] = compare_data

        return context

    def get_queryset(self):
        user = self.request.user
        userid = user.id

        roles = Role.objects.filter(user__id=userid)
        afs = AF.objects.filter(afOwningUser__id=userid)

        data, gf_count, tf_count = User.retrieve_related_rights(User, user, roles, afs, False)

        self.extra_context['role_count'] = roles.count()
        self.extra_context['af_count'] = afs.count()
        self.extra_context['gf_count'] = gf_count
        self.extra_context['tf_count'] = tf_count
        return list(data)

class Users(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name='myRDB/users.html'

    def get(self, request):
        queryset = User.objects.all()
        print(queryset)
        return Response({'users':queryset})

class Profile(generic.ListView):
    model = User
    template_name = 'myRDB/profile.html'
    paginate_by = 10
    context_object_name = "table_data"
    extra_context = {}

    def get_queryset(self):
        user = self.request.user
        userid = user.id

        roles = Role.objects.filter(user__id=userid)
        afs = AF.objects.filter(afOwningUser__id=userid)

        data, gf_count, tf_count = User.retrieve_related_rights(User, user, roles, afs, False)
        self.extra_context['role_count'] = roles.count()
        self.extra_context['af_count'] = afs.count()
        self.extra_context['gf_count'] = gf_count
        self.extra_context['tf_count'] = tf_count

        return list(data)
        # return tfList

    def autocompleteModel(request):
        if request.is_ajax():
            q = request.GET.get('term', '').capitalize()
            search_qs = User.objects.filter(name__startswith=q)
            results = []
            print(q)
            for r in search_qs:
                results.append(r.FIELD)
            data = json.dumps(results)
        else:
            data = 'fail'
        mimetype = 'application/json'
        return HttpResponse(data, mimetype)


# Create your views here.
class CSVtoMongoDB(generic.FormView):
    template_name = 'myRDB/csvToMongo.html'
    form_class = SomeForm
    success_url = '#'

    def form_valid(self, form):
        self.start_import_action()
        return super().form_valid(form)

    def start_import_action(self):
        firstline = True
        # TODO: dateiimportfield und pfad müssen noch verbunden werden!
        with open("myRDB/static/myRDB/data/Aus IIQ - User und TF komplett Neu_20180817_abMe.csv") as csvfile:
            csvreader = csv.reader(csvfile, delimiter=';', quotechar='"')
            for line in csvreader:
                if firstline == True:
                    firstline = False
                    pass
                else:
                    print(line)
                    orga = None
                    try:
                        orga = Orga.objects.get(team=line[8])
                    except(KeyError, Orga.DoesNotExist):
                        orga = Orga(team=line[8])
                    orga.save()

                    #
                    tf_application = None
                    try:
                        tf_application = TF_Application.objects.get(application_name=line[9])
                    except(KeyError, TF_Application.DoesNotExist):
                        tf_application = TF_Application(application_name=line[9])
                    tf_application.save()

                    tf = None
                    try:
                        tf = TF.objects.get(tf_name=line[3])
                    except(KeyError, TF.DoesNotExist):
                        tf = TF(tf_name=line[3], tf_description=line[4], highest_criticality_in_AF=line[7],
                                tf_owner_orga=orga, tf_application=tf_application, criticality=line[10])
                    tf.save()

                    gf = None
                    try:
                        gf = GF.objects.get(gf_name=line[11])
                    except(KeyError, GF.DoesNotExist):
                        gf = GF(gf_name=line[11], gf_description=line[12])
                        gf.save()
                    gf.tfs.add(tf)
                    gf.save()

                    af = None
                    try:
                        af = AF.objects.get(af_name=line[5])
                    except(KeyError, AF.DoesNotExist):
                        # TODO: Daten werden noch nicht korreckt eingetragen -> immer Null

                        if line[15] == "" and line[16] == "" and line[17] == "":
                            af = AF(af_name=line[5], af_description=line[6])
                        if line[15] != "" and line[16] == "" and line[17] == "":
                            af = AF(af_name=line[5], af_description=line[6]
                                    , af_valid_from=datetime.strptime(line[15], "%d.%m.%Y").isoformat())
                        if line[15] != "" and line[16] != "" and line[17] == "":
                            af = AF(af_name=line[5], af_description=line[6]
                                    , af_valid_from=datetime.strptime(line[15], "%d.%m.%Y").isoformat()
                                    , af_valid_till=datetime.strptime(line[16], "%d.%m.%Y").isoformat())
                        if line[15] != "" and line[16] != "" and line[17] != "":
                            af = AF(af_name=line[5], af_description=line[6],
                                    af_valid_from=datetime.strptime(line[15], "%d.%m.%Y").isoformat(),
                                    af_valid_till=datetime.strptime(line[16], "%d.%m.%Y").isoformat(),
                                    af_applied=datetime.strptime(line[17], "%d.%m.%Y").isoformat())
                        if line[15] == "" and line[16] != "" and line[17] != "":
                            af = AF(af_name=line[5], af_description=line[6]
                                    , af_valid_till=datetime.strptime(line[16], "%d.%m.%Y").isoformat()
                                    , af_applied=datetime.strptime(line[17], "%d.%m.%Y").isoformat())
                        if line[15] == "" and line[16] == "" and line[17] != "":
                            af = AF(af_name=line[5], af_description=line[6]
                                    , af_applied=datetime.strptime(line[17], "%d.%m.%Y").isoformat())
                    af.save()
                    af.gfs.add(gf)

                    user = None
                    try:
                        user = User.objects.get(identity=line[0])
                        if user.name != line[1]:
                            user.name = line[1]
                        if user.first_name != line[2]:
                            user.first_name = line[2]
                        if user.username != line[0]:
                            user.username = line[0]
                    except(KeyError, User.DoesNotExist):
                        user = User(identity=line[0], name=line[1], first_name=line[2], username=line[0])
                    user.save()
                    user.direct_connect_afs.add(af)


class IndexView(generic.ListView):
    template_name = 'myRDB/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        return Question.objects.order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'myRDB/detail.html'


class ResultView(generic.DetailView):
    model = Question
    template_name = 'myRDB/results.html'


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except(KeyError, Choice.DoesNotExist):
        return render(request, 'myRDB/detail.html',
                      {'question': question, 'error_message': "You didnt select any choice", })
    else:
        selected_choice.votes = F('votes') + 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('myRDB:results', args=(question.id,)))
