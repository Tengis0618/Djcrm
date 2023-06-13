from typing import Any, Dict
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from .models import Lead, Agent, Category
from .forms import LeadForm, LeadModelForm, CustomUserCreationForm, AssignAgentForm, LeadCategoryUpdateForm
from django.core.mail import send_mail
from agents.mixins import OrganiserAndLoginRequiredMixin

# Create your views here.

class SignupView(generic.CreateView):
    template_name = 'registration/signup.html'
    form_class = CustomUserCreationForm

    def get_success_url(self):
        return '/leads'

class LandingPageView(generic.TemplateView):
    template_name = 'landing.html'

def landing_page(request):
    return render(request, 'landing.html')

class LeadListView(LoginRequiredMixin, generic.ListView):
    template_name = 'home_page.html'
    context_object_name = 'leads'

    def get_queryset(self):
        user = self.request.user
        if user.is_organiser:
            queryset = Lead.objects.filter(organisation = user.userprofile,  agent__isnull =False)
        else:
            queryset = Lead.objects.filter(organisation = user.agent.organisation, agent__isnull =False)
            queryset = queryset.filter(agent__user = user)
        return queryset
    
    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super(LeadListView, self).get_context_data(**kwargs)
        if user.is_organiser:
            queryset = Lead.objects.filter(organisation = user.userprofile, agent__isnull = True)
            context.update({
                'unassigned_leads':queryset
            })
        return context

def leads_list(request):
    leads= Lead.objects.all()
    context = {
        'leads': leads
    }
    return render(request, 'home_page.html', context)

class LeadDetailView(LoginRequiredMixin, generic.DetailView):
    
    template_name = 'lead_list.html'
    context_object_name = 'lead'

    def get_queryset(self):
        user = self.request.user
        if user.is_organiser:
            queryset = Lead.objects.filter(organisation = user.userprofile)
        else:
            queryset = Lead.objects.filter(organisation = user.agent.organisation)
            queryset = queryset.filter(agent__user = user)
        return queryset

def lead_detail(request, pk):
    leads = Lead.objects.filter(id = pk)
    context = {
        'leads': leads
    }
    return render(request, 'lead_list.html', context)
'''
def lead_create(request):
    form = LeadForm()
    if request.method =='POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            age = form.cleaned_data['age']
            agent = Lead.objects.first()
            Lead.objects.create(first_name = first_name, last_name = last_name, age=age, agent = agent)
            return redirect('/leads')
    context = {
        'form': LeadForm()
    }
    return render(request, 'lead_create.html', context)
'''

def lead_create(request):
    form = LeadModelForm()
    if request.method =='POST':
        form = LeadModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/leads')
    context = {
        'form': LeadModelForm()
    }
    return render(request, 'lead_create.html', context)

class LeadCreateView(OrganiserAndLoginRequiredMixin,generic.CreateView):
    template_name = 'lead_create.html'
    form_class = LeadModelForm
    def get_success_url(self):
        return reverse("leads")
    
    def form_valid(self, form):
        lead = form.save(commit=False)
        lead.organisation = self.request.user.userprofile
        lead.save()
        #Send email
        send_mail(
            subject='New Lead Created',
            message='Direct to the leads list to view the lead',
            from_email='test@test.com',
            recipient_list=['tengis0618@gmail.com']
            )
        return super(LeadCreateView, self).form_valid(form)

def lead_update(request, pk):
    lead = Lead.objects.get(id = pk)
    form = LeadModelForm(instance=lead)
    if request.method =='POST':
        form = LeadModelForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            return redirect('/leads')
    context = {
        'lead': lead,
        'form': form
    }
    return render(request, 'lead_update.html', context)

class LeadUpdateView(OrganiserAndLoginRequiredMixin,generic.UpdateView):
    template_name = 'lead_update.html'
    form_class = LeadModelForm

    def get_success_url(self):
        return "/leads"
    
    def get_queryset(self):
        user = self.request.user
        return Lead.objects.filter(organisation = user.userprofile)

'''
def lead_update(request, pk):
    lead = Lead.objects.get(id = pk)
    form = LeadForm()
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            age = form.cleaned_data['age']
            lead.first_name = first_name
            lead.last_name = last_name
            lead.age = age
            lead.save()
            return redirect('/leads/')
    context = {
        'lead': lead,
        'form': form
    }
    return render(request, 'lead_update.html', context)
'''

def lead_delete(request, pk):
    lead = Lead.objects.get(id=pk)
    lead.delete()
    return redirect('/leads')

class LeadDeleteView(OrganiserAndLoginRequiredMixin, generic.DeleteView):
    template_name = 'lead_delete.html'
    def get_success_url(self):
        return "/leads"
    
    def get_queryset(self):
        user = self.request.user
        return Lead.objects.filter(organisation = user.userprofile)
    
class AssignAgentView(OrganiserAndLoginRequiredMixin, generic.FormView):
    template_name = 'assign_agent.html'
    form_class = AssignAgentForm

    def get_form_kwargs(self, **kwargs):
        kwargs = super(AssignAgentView, self).get_form_kwargs(**kwargs)
        kwargs.update({
            'request':self.request
        })
        return kwargs

    def get_success_url(self):
        return reverse('leads')
    
    def form_valid(self, form):
        agent = form.cleaned_data['agent']
        lead = Lead.objects.get(id = self.kwargs['pk'])
        lead.agent = agent
        lead.save()
        return super(AssignAgentView, self).form_valid(form)
    
class CategoryListView(LoginRequiredMixin, generic.ListView):
    template_name = 'category_list.html'
    context_object_name = 'category_list'

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        user = self.request.user
        if user.is_organiser:
            queryset = Lead.objects.filter(organisation = user.userprofile)
        else:
            queryset = Lead.objects.filter(organisation = user.agent.organisation)
        context.update ({
            'unassigned_lead_count': queryset.filter(category__isnull = True).count()
        })
        return context
    
    def get_queryset(self):
        user = self.request.user
        if user.is_organiser:
            queryset = Category.objects.filter(organisation = user.userprofile)
        else:
            queryset = Category.objects.filter(organisation = user.agent.organisation)
        return queryset
    
class CategoryDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = 'category_detail.html'
    context_object_name = 'category'


    def get_queryset(self):
        user = self.request.user
        if user.is_organiser:
            queryset = Category.objects.filter(organisation = user.userprofile)
        else:
            queryset = Category.objects.filter(organisation = user.agent.organisation)
        return queryset
    
class LeadCategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'lead_category_update.html'
    form_class = LeadCategoryUpdateForm

    def get_success_url(self):
        return reverse('lead_detail', kwargs = {'pk': self.get_object().id})
    
    def get_queryset(self):
        user = self.request.user
        if user.is_organiser:
            queryset = Lead.objects.filter(organisation = user.userprofile)
        else:
            queryset = Lead.objects.filter(organisation = user.agent.organisation)
        return queryset
    
        