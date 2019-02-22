from django.shortcuts import render
from django_tables2 import RequestConfig
from .forms import SharedMusicLinkForm

from .models import SharedMusicLink, User, UserInfo, Friends
from .tables import SharedLinksTable
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.db.utils import DatabaseError
from django.contrib.auth import logout as auth_logout
from urllib.request import urlopen
import json
import django_filters

PROVIDER = 'facebook'


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
        social_user = request.user.social_auth.get(provider=PROVIDER)
        userid = social_user.uid
        name = social_user.extra_data['name']
        first_name = social_user.extra_data['first_name']
        last_name = social_user.extra_data['last_name']
        email = social_user.extra_data['email']

        #storing user information
        user, created = User.objects.update_or_create(user_id=userid)
        userInfo, created = UserInfo.objects.update_or_create(
            user=user,
            defaults={'name': name, 'first_name': first_name, 'last_name': last_name, 'email': email}
        )

        url = u'https://graph.facebook.com/{0}/' \
              u'friends?fields=id,name' \
              u'&access_token={1}'.format(userid, social_user.extra_data['access_token'])

        friends = json.loads(urlopen(url).read()).get('data')
        for friend in friends:
            friend_id = friend['id']
            friend_user, created = User.objects.update_or_create(user_id=friend_id)
            userFriend, created = Friends.objects.get_or_create(user=user)
            userFriend.friends_id.add(friend_user)

        latest_stored_links = SharedMusicLink.objects.filter(status=status,user_id=userid).order_by('-shared_date')
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
            sharedLink.user_id = request.user.social_auth.get(provider=PROVIDER).uid
            try:
                sharedLink.save()
            except DatabaseError as e:
                raise form.ValidationError(e)
            return HttpResponseRedirect(reverse('showList', args=(),kwargs={'status': status}))
    else:
        form = SharedMusicLinkForm(instance=musicLink)
    return render(request, 'storeLinks/sharedMusicLinkForm.html', {'form': form})
