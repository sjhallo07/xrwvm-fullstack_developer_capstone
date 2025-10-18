
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from datetime import datetime

from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .restapis import get_request, analyze_review_sentiments, post_review
# from .populate import initiate


# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
from .models import CarMake, CarModel
from .populate import initiate

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

@csrf_exempt
def get_cars(request):
    count = CarMake.objects.filter().count()
    print(count)
    if(count == 0):
        initiate()
    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for car_model in car_models:
        cars.append({"CarModel": car_model.name, "CarMake": car_model.car_make.name})
    return JsonResponse({"CarModels":cars})

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def logout_user(request):
    logout(request)  # Terminate user session
    data = {"userName": ""}  # Return empty username
    return JsonResponse(data)



@csrf_exempt
def registration(request):
    if request.method == "POST":
        # Load JSON data from the request body
        data = json.loads(request.body)
        username = data['userName']
        password = data['password']
        first_name = data['firstName']
        last_name = data['lastName']
        email = data['email']
        username_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            username_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug(f"{username} is new user")
        # If it is a new user
        if not username_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password, email=email)
            # Login the user and redirect to list page
            login(request, user)
            data = {"userName": username, "status": "Authenticated"}
            return JsonResponse(data)
        else:
            data = {"userName": username, "error": "Already Registered"}
            return JsonResponse(data)
    else:
        return JsonResponse({"error": "POST request required"}, status=400)

# # Update the `get_dealerships` view to render the index page with
# a list of dealerships
#Update the `get_dealerships` render list of dealerships all by default, particular state if state is passed
def get_dealerships(request, state="All"):
    if(state == "All"):
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/"+state
    dealerships = get_request(endpoint)
    if dealerships is None:
        return JsonResponse({"status":502, "message":"Backend service unavailable"}, status=502)
    return JsonResponse({"status":200,"dealers":dealerships})
# ...

# Create a `get_dealer_reviews` view to render the reviews of a dealer
def get_dealer_reviews(request, dealer_id):
    # if dealer id has been provided
    if(dealer_id):
        endpoint = "/fetchReviews/dealer/"+str(dealer_id)
        reviews = get_request(endpoint)
        if reviews is None:
            return JsonResponse({"status":502, "message":"Reviews service unavailable"}, status=502)
        # Ensure reviews is iterable
        safe_reviews = []
        for review_detail in reviews:
            try:
                text = review_detail.get('review', '') if isinstance(review_detail, dict) else ''
                response = analyze_review_sentiments(text)
                sentiment = None
                if isinstance(response, dict):
                    sentiment = response.get('sentiment', 'neutral')
                else:
                    sentiment = 'neutral'
                # attach sentiment
                if isinstance(review_detail, dict):
                    review_detail['sentiment'] = sentiment
                    safe_reviews.append(review_detail)
            except Exception as err:
                # skip malformed review entries but continue
                print(f"Error processing review detail: {err}")
        return JsonResponse({"status":200,"reviews":safe_reviews})
    else:
        return JsonResponse({"status":400,"message":"Bad Request"})
# ...

# Create a `get_dealer_details` view to render the dealer details
def get_dealer_details(request, dealer_id):
    if(dealer_id):
        endpoint = "/fetchDealer/"+str(dealer_id)
        dealership = get_request(endpoint)
        if dealership is None:
            return JsonResponse({"status":502, "message":"Dealer service unavailable"}, status=502)
        return JsonResponse({"status":200,"dealer":dealership})
    else:
        return JsonResponse({"status":400,"message":"Bad Request"})
# ...

# Create a `add_review` view to submit a review
def add_review(request):
    if(request.user.is_anonymous == False):
        data = json.loads(request.body)
        response = post_review(data)
        if response:
            return JsonResponse({"status":200})
        else:
            return JsonResponse({"status":502, "message":"Error in posting review"}, status=502)
    else:
        return JsonResponse({"status":403,"message":"Unauthorized"})
# ...
