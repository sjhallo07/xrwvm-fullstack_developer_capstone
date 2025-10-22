import requests
from django.conf import settings
from django.http import JsonResponse, HttpResponseServerError
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from requests.utils import requote_uri

DEALERS_SERVICE = getattr(settings, "DEALERS_SERVICE_URL", "http://express-service:3000")
SENTIMENT_SERVICE = getattr(settings, "SENTIMENT_SERVICE_URL", "http://sentiment:8080")

@require_GET
def fetch_dealers(request):
    try:
        r = requests.get(f"{DEALERS_SERVICE}/fetchDealers", timeout=10)
        r.raise_for_status()
        return JsonResponse(r.json(), safe=False)
    except requests.RequestException as e:
        return HttpResponseServerError(f"Error fetching dealers: {e}")

@require_GET
def fetch_dealer_by_id(request, dealer_id):
    try:
        r = requests.get(f"{DEALERS_SERVICE}/fetchDealer/{dealer_id}", timeout=10)
        r.raise_for_status()
        return JsonResponse(r.json(), safe=False)
    except requests.RequestException as e:
        return HttpResponseServerError(f"Error fetching dealer: {e}")

@require_GET
def fetch_reviews_for_dealer(request, dealer_id):
    try:
        r = requests.get(f"{DEALERS_SERVICE}/fetchReview/dealer/{dealer_id}", timeout=10)
        r.raise_for_status()
        reviews = r.json()
        for rev in reviews if isinstance(reviews, list) else []:
            text = rev.get("review", "")
            if text:
                try:
                    s = requests.get(f"{SENTIMENT_SERVICE}/analyze/{requote_uri(text)}", timeout=5)
                    if s.ok:
                        rev["_sentiment"] = s.json()
                except requests.RequestException:
                    rev["_sentiment"] = {"error": "sentiment-unavailable"}
        return JsonResponse(reviews, safe=False)
    except requests.RequestException as e:
        return HttpResponseServerError(f"Error fetching reviews: {e}")

@csrf_exempt
@require_POST
def insert_review(request):
    try:
        payload = request.body
        r = requests.post(f"{DEALERS_SERVICE}/insertReview", data=payload, headers={"Content-Type": "application/json"}, timeout=10)
        r.raise_for_status()
        return JsonResponse(r.json(), safe=False, status=r.status_code)
    except requests.RequestException as e:
        return HttpResponseServerError(f"Error inserting review: {e}")
