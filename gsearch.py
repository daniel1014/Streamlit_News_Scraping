from googleapiclient.discovery import build
import ssl
import urllib.request

my_api_key = "AIzaSyAWd9YsJLvzIiQViBppiiy9L3w_osvsuyU" # Save as environment variable in Azure secret later
my_api_key_backup = "AIzaSyD3A7DAN2PxdzCkHnwFIBd8mVTUHl25bLY"   # Backup
my_cse_id = "c7176b7cccea54d9d" # Save as environment variable in Azure secret later

# Create an unverified SSL context to ignore certificate errors (e.g. SSL: CERTIFICATE_VERIFY_FAILED)
ssl_context = ssl._create_unverified_context()

def google_search(search_term, date_restrict=None, gl=None, num=int, **kwargs):
    try:
        # Use this context when building the service
        service = build("customsearch", "v1", developerKey=my_api_key, http=urllib.request.build_opener(urllib.request.HTTPSHandler(context=ssl_context)))
        res = service.cse().list(q=search_term, cx=my_cse_id, dateRestrict=date_restrict, gl=gl, num=num, **kwargs).execute()
    except:
        service = build("customsearch", "v1", developerKey=my_api_key_backup)
        res = service.cse().list(q=search_term, cx=my_cse_id, dateRestrict=date_restrict, gl=gl, num=num, **kwargs).execute()
    return res['items'] if 'items' in res else []