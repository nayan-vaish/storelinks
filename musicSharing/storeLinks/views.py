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
from django.core.mail import EmailMultiAlternatives
import django_filters

PROVIDER = 'facebook'


class SharedLinkFilter(django_filters.FilterSet):
    link_name = django_filters.CharFilter(lookup_expr='icontains')
    link_source = django_filters.CharFilter(lookup_expr='istartswith')
    shared_by = django_filters.CharFilter(lookup_expr='istartswith')
    artist_name = django_filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = SharedMusicLink
        fields = ['link_name', 'artist_name', 'link_source', 'shared_by', 'link_type']


def logout(request):
    """Logs out user"""
    auth_logout(request)
    return HttpResponseRedirect(reverse('login', args=()))


def login(request):
    return render(request, 'storeLinks/login.html')


def createSubject(senderName, linkName):
    subject = senderName + " shared " + linkName + " via MusicShare."
    return subject


def createTextBody(senderName, link):
    textBody = senderName + " has shared " + link + "\n"
    textBody = textBody + "Keep Listening! Keep Sharing!"
    return textBody


def createHtmlBody(senderName, link, linkName):
    htmlBody = "<span><h4>" + senderName + "</h4>"
    htmlBody += "<p> has shared:</p></span>"
    htmlBody += "<a href=" + link + ">" + linkName + "</a>"
    htmlBody += "Keep Listening! Keep Sharing!"
    return htmlBody


def shareLink(request, status, id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login', args=()))
    else:
        social_user = request.user.social_auth.get(provider=PROVIDER)
        userid = social_user.uid
        user = User.objects.get(user_id=userid)
        ## do seccurity check
        musicLink = SharedMusicLink.objects.get(pk=id)
        print(musicLink)
        if user:
            try:
                friends = Friends.objects.get(user=user)
                print(friends)
                userInfo = UserInfo.objects.get(user=user)

                listOfFriendEmails = []
                for friend in friends.friends_id.all():
                    print("sharing with = " + str(friend.user_id) + "link = " + str(musicLink.link))
                    sharedLink, created = SharedMusicLink.objects.get_or_create(
                    user_id=friend.user_id, link=musicLink.link,
                    defaults={'link_name': musicLink.link_name, 'artist_name': musicLink.artist_name, 'link_source': musicLink.link_source, 'link_type': musicLink.link_type, 'shared_by': userInfo.name}
                    )
                    print("printing shared link" + sharedLink.link_name + " " + str(sharedLink.user_id) + " " + sharedLink.link)
                    if not created:
                        print("link already shared")
                    else:
                        friendUser = User.objects.get(user_id=friend.user_id)
                        friendInfo = UserInfo.objects.get(user=friendUser)
                        listOfFriendEmails.append(friendInfo.email)

                        if listOfFriendEmails:
                            print("sending email")
                            senderEmail = userInfo.email
                            subject = createSubject(userInfo.name, sharedLink.link_name)
                            textBody = createTextBody(userInfo.name, sharedLink.link)
                            htmlBody = createHtmlBody(userInfo.name, sharedLink.link, sharedLink.link_name)
                            msg = EmailMultiAlternatives(subject, textBody, senderEmail, listOfFriendEmails)
                            msg.attach_alternative(htmlBody, "text/html")
                            msg.send()

                        else:
                            print("user not found")
            except Exception as e:
                print(e)

        return HttpResponseRedirect(reverse('showList', args=(),kwargs={'status': status, 'shared': str(musicLink.link_name)}))


def showList(request, status=1, shared=''):
    if request.user.is_authenticated:
        social_user = request.user.social_auth.get(provider=PROVIDER)
        userid = social_user.uid
        name = social_user.extra_data['name']
        first_name = social_user.extra_data['first_name']
        last_name = social_user.extra_data['last_name']
        email = social_user.extra_data['email']
        print(userid)

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
        if shared:
            # 75 is max length of link name to be displayed when shared
            shared = shared[:75] + (shared[75:] and '...')
        context = {'table': table, 'status': status, 'filter': filter, 'shared': shared.title()}
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
