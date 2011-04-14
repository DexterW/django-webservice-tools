from piston.handler import BaseHandler
from webservice_tools import  utils
from webservice_tools.decorators import login_required
from webservice_tools.apps.friends.models import FriendRequest, FriendGroup
from django.db import models
from django.conf import settings
app_label, model_name = settings.AUTH_PROFILE_MODULE.split('.')
PROFILE_MODEL = models.get_model(app_label, model_name)


class FriendsHandler(BaseHandler):
    allowed_methods = ('GET', 'DELETE')
    
    @login_required
    def read(self, request, response):
        """
        Return a list of the users friends
        """
        profile = request.user.get_profile()
        friends = profile.friends.all()
        response.set(friends=[p.dict() for p in friends])
        return response.send()
    
    @login_required
    def delete(self, request, id, response):
        """
        Remove a friend from your list of friends
        """
        profile = request.user.get_profile()
        
        try:
            friend = PROFILE_MODEL.objects.get(id=id)
        except PROFILE_MODEL.DoesNotExist:
            return response.send(status=404)
        
        profile.friends.remove(friend)
        return response.send()
        
        

class FriendRequestHandler(BaseHandler):
    allowed_methods = ('POST', 'GET', 'PUT', 'DELETE')
    
    
    @login_required
    def create(self, request, id, response):
        """
        Create a new friend request
        Params:
          id [id]: id of the friend being requested
          message [string] (optional): message to send to the friend
        """
        request_from = request.user.get_profile()
        message = request.GET.get('message', '')

        
        try:
            request_to = PROFILE_MODEL.objects.get(id=id)
        except PROFILE_MODEL.DoesNotExist:
            return response.send(status=404)
        
        if request_to in request_from.friends.all():
            return response.send(errors='That user is already in your friends list')
        
        try:
            FriendRequest.objects.get(request_to=request_to, request_from=request_from)
            return response.send(errors="You have already sent this user a friend request")
        except FriendRequest.DoesNotExist:
            pass
        
        try:
            FriendRequest.objects.get(request_from=request_to, request_to=request_from)
            return response.send(errors="This person has already invited you as a friend.")
        except FriendRequest.DoesNotExist:
            pass
        
        FriendRequest.objects.create(request_from=request_from, request_to=request_to, message=message)
        return response.send(status=201)
    
    @login_required
    def read(self, request, response):
        """
        Return a list of the users' current friend requests
        """
        profile = request.user.get_profile()
        pending_requests = FriendRequest.objects.filter(request_to=profile)
        outgoing_requests = FriendRequest.objects.filter(request_from=profile)
        response.set(pending_requests=pending_requests, outgoing_requests=outgoing_requests)
        return response.send()
    
    @login_required
    def update(self, request, id, response):
        """
        Resolve a pending friend request
        Params:
           id [id] friend request id
           accept [boolean] accept or reject? (optional, defaults to True)
        """
        profile = request.user.get_profile()
        try:
            friend_request = FriendRequest.objects.get(id=id, request_to=request.user.get_profile())
        except FriendRequest.DoesNotExist:
            return response.send(status=404)
        
        accept = utils.strToBool(request.PUT.get('accept', 'True'))
        
        if accept:
            profile.friends.add(friend_request.request_from)
        
        friend_request.delete()
        return response.send()
    
    @login_required
    def delete(self, request, id, response):
        """
        Delete a friend request, (can only be done by requestor, requestee must update with accept=false)
        Params:
           id [id] friend request id
        """
        profile = request.user.get_profile()
        try:
            friend_request = FriendRequest.objects.get(id=id, request_from=profile)
        except FriendRequest.DoesNotExist:
            return response.send(status=404)
        
        friend_request.delete()
        return response.send()
        

class GroupHandler(BaseHandler):
    allowed_method = ('GET', 'DELETE', 'POST')
    
    @login_required
    def read(self, request, id, response):
        """
        Get a group's details by ID
        """
        profile = request.user.get_profile()
        try:
            friendgroup = FriendGroup.objects.get(id=id, owner=profile)
        except FriendGroup.DoesNotExist:
            return response.send(errors="Group with ID %s does not exist" % id,
                                 status=404)
        
        members = [profile.dict() for profile in friendgroup.members.all()]
        response.set(name=friendgroup.name, members = members)
        return response.send()
    
    @login_required
    def create(self, request, response):
        """
        Create a new Group
        Params:
            @name: name of the new group
        """
        profile = request.user.get_profile()
        name = request.POST.get("name")
        
        #verify that the given name is unique
        try:
            FriendGroup.objects.get(name=name, owner=profile)
            return response.send(errors="You already have a group with the name %s" % name, status=499)
        except FriendGroup.DoesNotExist:
            pass
        
        new_group = FriendGroup.objects.create(name=name,  owner=profile)
        response.set(new_group_id=new_group.id, new_group_name=new_group.name)
        return response.send()
        
    
    @login_required
    def update(self, request, group_id, friend_id, response):
        """
        Add/remove a user from a friend group
        PUT Params:
          action [string] 'add' or 'remove' person from group (optional, defaults to add)
        """
        profile = request.user.get_profile()
        action = request.PUT.get('action', 'add')
        try:
            friendgroup = FriendGroup.objects.get(id=id, owner=profile)
        except FriendGroup.DoesNotExist:
            return response.send(errors="Group with ID %s does not exist" % id,
                                 status=404)
        
        try:
            friend = PROFILE_MODEL.objects.get(id=friend_id)
        except PROFILE_MODEL.DoesNotExist:
            return response.send(errors="No such user", status=404)
        
        if friend in profile.friends.all():
            if action == 'add':
                friendgroup.members.add(profile)
            elif action == 'remove':
                friendgroup.members.remove(profile)
                
        return response.send()
        
    
    @login_required
    def delete(self, request, id, response):
        """
        Delete a group
        """
        profile = request.user.get_profile()
        try:
            friendgroup = FriendGroup.objects.get(id=id, owner=profile)
        except FriendGroup.DoesNotExist:
            return response.send(status=404)
        
        friendgroup.delete()
        return response.send(status=200)

class GroupsHandler(BaseHandler):
    allowed_methods = ('GET',)        

    @login_required
    def read(self, request, response):
        """
        Get the groups of the logged in user
        """
        profile = request.user.get_profile()
        friend_groups = FriendGroup.objects.filter(owner=profile)
        result = [{'name': f.name, 'id': f.id} for f in friend_groups]
        response.set(groups=result)
        return response.send()
      
        
