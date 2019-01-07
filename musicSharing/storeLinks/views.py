from django.shortcuts import render
from django_tables2 import RequestConfig
from .forms import SharedMusicLinkForm

from .models import SharedMusicLink
from .tables import SharedLinksTable
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.db.utils import DatabaseError
from django.contrib.auth import logout as auth_logout
import django_filters


class SharedLinkFilter(django_filters.FilterSet):
    link_source = django_filters.CharFilter(lookup_expr='iexact')
    shared_by = django_filters.CharFilter(lookup_expr='iexact')
    artist_name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = SharedMusicLink
        fields = ['artist_name', 'link_source', 'shared_by', 'link_type']


def logout(request):
    """Logs out user"""
    auth_logout(request)
    return HttpResponseRedirect(reverse('login', args=()))


def login(request):
    return render(request, 'storeLinks/login.html')


def showList(request, status=1):
    if request.user.is_authenticated:
        username = request.user.username
        print(username)
        latest_stored_links = SharedMusicLink.objects.filter(status=status,user_name=username).order_by('-shared_date')
        filter = SharedLinkFilter(request.GET, queryset=latest_stored_links)
        table = SharedLinksTable(filter.qs)
        RequestConfig(request).configure(table)
        context = {'table': table, 'status': status, 'filter': filter}
        return render(request, 'storeLinks/showList.html', context)
    else:
        return HttpResponseRedirect(reverse('login', args=()))


def deleteLink(request, status, id):
    if request.user.is_authenticated:
        SharedMusicLink.objects.filter(id=id).delete()
        return HttpResponseRedirect(reverse('showList', args=(),kwargs={'status': status}))
    else:
        return HttpResponseRedirect(reverse('login', args=()))


def changeStatusofLink(request, current_status, to_status, id):
    if request.user.is_authenticated:
        SharedMusicLink.objects.filter(id=id).update(status=to_status)
        return HttpResponseRedirect(reverse('showList', args=(),kwargs={'status': current_status}))
    else:
        return HttpResponseRedirect(reverse('login', args=()))


def manageSharedLinks(request, status, id=None):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login', args=()))
    musicLink = None
    if id != None:
        musicLink = SharedMusicLink.objects.get(pk=id)
    if request.method == 'POST':
        form = SharedMusicLinkForm(request.POST, instance=musicLink)
        if form.is_valid():
            sharedLink = form.save(commit=False)
            sharedLink.status = status
            sharedLink.user_name = request.user.username
            try:
                sharedLink.save()
            except DatabaseError as e:
                raise form.ValidationError(e)
            return HttpResponseRedirect(reverse('showList', args=(),kwargs={'status': status}))
    else:
        form = SharedMusicLinkForm(instance=musicLink)
    return render(request, 'storeLinks/sharedMusicLinkForm.html', {'form': form})
