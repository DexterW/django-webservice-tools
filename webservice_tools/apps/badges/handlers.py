import sys
from webservice_tools.utils import BaseHandler
import datetime
from piston.handler import BaseHandler
from webservice_tools.decorators import login_required
from webservice_tools.response_util import ResponseObject
from webservice_tools import utils
from django.db import models
from webservice_tools.apps.badges.models import BadgeToUser, BadgeModel, consts
from django.conf import settings
app_label, model_name = settings.AUTH_PROFILE_MODULE.split('.')
PROFILE_MODEL = models.get_model(app_label, model_name)

class BadgeHandler(BaseHandler):
    allowed_methods = ('GET',)
    @login_required
    def read(self, request, id, response):
        """
        Return a list of all badges and whether or not this user has won them
        API Handler: GET /badges/{id}
        
        Returns:
            @name [string] name of the badge
            @description [string] description of the badge 
            @won_description [string] past tense description after the badge is won
            @image_url [url] image for the badge
            @hi_res_image_url [url] url of the hi res image for the badge
            @thumb_url [url] thumbnail image for the badge
            @hi_res_thumb_url [url] hi res thumbnail image 
            @id [id] id of the badge 
            @order [integer] order, entered by users, allowing them to order badges on the screein 
            @won [bool] has the user won the badge? 
            @won_count [integer] number of times the badge has by won by this user 
        """
        all_badges = BadgeModel.objects.all()
        try:
            profile = PROFILE_MODEL.objects.get(id=id)
        except PROFILE_MODEL.DoesNotExist:
            return response.send(errors="Not found", status=404)
        users_badges = [b.badge for b in BadgeToUser.objects.filter(winner=profile)]
        
        ret = []
        for badge in all_badges:
                ret.append({'name': badge.name,
                            'id': badge.id,
                            'description': badge.description,
                            'won_description': badge.won_description,
                            'images': badge.images,
                            'order': badge.badge_order,
                            'won_count': len([b for b in users_badges if b == badge]),
                            'won': badge in users_badges})
                
        response.set(badges=ret)
        return response.send()


class BadgesWonCountHandler(BaseHandler):
    allowed_methods=('GET',)
    
    @login_required
    def read(self, request, response):
        """
        Return a count of badges won since a certain date
        API Handler: GET /badges/count
        Params:
           @since [datetime] format "2011-12-25 18:22:11.123822" 
        
        Returns:
           @count [number] number of times the user has won this particular badge
           @timestamp [timestamp] current server timestamp (for use with 'since')
        """
        profile = request.user.get_profile()
        since = request.GET.get('since')
        since = utils.default_time_parse(since)
        since = since or datetime.datetime(1970, 1, 1)
        now  = datetime.datetime.utcnow()
        count = BadgeToUser.objects.filter(winner=profile, when_created__gte=since).count()
        response.set(count=count, timestamp=now.strftime("%Y-%m-%d %H:%M:%S.%f"))
        return response.send()
    
#ALL DEFINITION EOF
module_name = globals().get('__name__')
handlers = sys.modules[module_name]
handlers._all_ = []
for handler_name in dir():
    m = getattr(handlers, handler_name)
    if type(m) == type(BaseHandler):
        handlers._all_.append(handler_name)