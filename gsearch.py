from googleapiclient.discovery import build

my_api_key = "AIzaSyAWd9YsJLvzIiQViBppiiy9L3w_osvsuyU" # Save as environment variable in Azure secret later
my_api_key_backup = "AIzaSyD3A7DAN2PxdzCkHnwFIBd8mVTUHl25bLY"   # Backup
my_cse_id = "c7176b7cccea54d9d" # Save as environment variable in Azure secret later

def google_search(search_term, date_restrict=None, gl=None, **kwargs):
    try:
        service = build("customsearch", "v1", developerKey=my_api_key)
        res = service.cse().list(q=search_term, cx=my_cse_id, dateRestrict=date_restrict, gl=gl, **kwargs).execute()
    except:
        service = build("customsearch", "v1", developerKey=my_api_key_backup)
        res = service.cse().list(q=search_term, cx=my_cse_id, dateRestrict=date_restrict, gl=gl, **kwargs).execute()
    return res['items'] if 'items' in res else []

