from django.utils.deprecation import MiddlewareMixin
from .models import Log
from django.db.models import F 

class RequestLogMiddleware(MiddlewareMixin):
 

    def process_request(self, request):
       
        method = request.method
        url = request.path

        updated = Log.objects.filter(
            method=method, url=url).update(count=F('count') + 1)
       

      
        if not updated:
            new_url=Log.objects.create(method=method, url=url, count=1)
          