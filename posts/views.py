from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic
from django.http import Http404
# pip install django-braces
from braces.views import SelectRelatedMixin
from . import models, forms
from .models import Post
from django.contrib.auth import get_user_model
from django.contrib import messages

# Create your views here.

User = get_user_model()


class PostList(SelectRelatedMixin, generic.ListView):
    queryset = Post.objects.all()
    models = models.Post
    select_related = ('user', 'group')


class UserPost(generic.ListView):
    models = models.Post
    template_name = 'posts/user_post_list.html'

    def get_queryset(self):
        try:
            self.post_user = User.objects.prefetch_related('posts').get(username__iexact=self.kwargs.get('username'))
        except User.DoesNotExist:
            raise Http404
        else:
            return self.post_user.posts.all()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_user'] = self.post_user
        return context


class PostDetail(SelectRelatedMixin, generic.DetailView):
    models = models.Post
    select_related = ('user', 'group')
    queryset = Post.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user__username__iexact=self.kwargs.get('username'))


class CreatePost(LoginRequiredMixin, generic.CreateView):
    models = models.Post
    fields = ('message', 'group')
    queryset = Post.objects.all()
    template_name = "posts/post_form.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     return queryset.filter(user_id=self.request.user.id)

class DeletePost(LoginRequiredMixin, SelectRelatedMixin, generic.DeleteView):
    models = models.Post
    select_related = ('user', 'group')
    success_url = reverse_lazy('posts:all')
    queryset = Post.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user_id=self.request.user.id)

    def delete(self, *args, **kwargs):
        messages.success = (self.request, 'Post Deleted')
        return super().delete(*args, **kwargs)