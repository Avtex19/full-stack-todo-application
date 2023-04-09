from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages

# Imports for Reordering Feature
from django.shortcuts import redirect

from .models import Task


# Create your views here.

class CustomLoginView(LoginView):
    template_name = 'myapp/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks')


class RegisterPage(FormView):
    template_name = 'myapp/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)  # Redirects to login page.
        return super(RegisterPage, self).form_valid(form)  # What we want to do here is once this form is submitted
        # once it is valid we just want to make sure the user is logged in

    def form_invalid(self, form):
        # Shows errors if passwords do not match, or passwords are too common or are entirely numeric or length is
        # less than 8,Shows if username is already taken.
        for errors in form.errors.values():
            for error in errors:
                print(error)
                messages.error(self.request, error)
        return super(RegisterPage, self).form_invalid(form)

    # we block authenticated user from register page.
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)  # if we have any other situation just go ahead and
        # continue on with what you were supposed to do here, so we will just throw in register page.


class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)  # Filter tasks for user and modify tasks
        # from data. It corresponds user's tasks to this user.
        context['count'] = context['tasks'].filter(complete=False).count()  # queryset count function

        search_input = self.request.GET.get('search-area') or ''
        if search_input:  # if we have some data here, lets go ahead and modify our search field here or our query set.
            context['tasks'] = context['tasks'].filter(
                title__contains=search_input)
            # filtering query set
        # whatever the form name was we want to take this
        # value the name of the form, we want to get that value and the input is either going to be that request or
        # it's going to be an empty string if we do not want to search anything

        context['search_input'] = search_input
        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'myapp/task.html'


class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')
    template_name = 'myapp/task-form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')
    template_name = 'myapp/task-form.html'


class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')
    template_name = 'myapp/task_confirm_delete.html'
