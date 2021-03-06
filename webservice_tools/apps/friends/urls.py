from django.conf.urls.defaults import *
from webservice_tools.utils import Resource
from webservice_tools.apps.friends.handlers import FriendsHandler, FriendRequestHandler, GroupHandler, GroupsHandler 
urlpatterns = patterns('',
    (r'^(?P<id>[\d]+)/?$', Resource(FriendsHandler)),
    (r'^requests/(?P<id>[\d]+)/?$', Resource(FriendRequestHandler)),
    (r'^requests/user/(?P<id>[\d]+)/?$', Resource(FriendRequestHandler)),
    (r'^requests/?$', Resource(FriendRequestHandler)),
    (r'^group/(?P<id>[\d]+)/?$', Resource(GroupHandler)),
    (r'^group/?$', Resource(GroupHandler)),
    (r'^group/(?P<group_id>[\d]+)/friend/(?P<friend_id>)/?$', Resource(GroupHandler)),
    (r'^groups/?$', Resource(GroupsHandler)),
    
)
