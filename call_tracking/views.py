from django.conf import settings
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, reverse
from django.template.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic import DetailView, ListView

from twilio.twiml.voice_response import VoiceResponse
from twilio.jwt.client import ClientCapabilityToken
from twilio.rest import Client

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .forms import AreaCodeForm, PurchaseNumberForm, CampaignForm, LeadSourceForm, AddExistingNumberForm
from .models import Campaign, LeadSources, Lead, Call, PurchasedNumbers
from .utils import search_phone_numbers, purchase_phone_number


#trying to serialize call queryset as json to return in vue template
from django.core.serializers import serialize
from django.core import serializers

# Home page view and JSON views to power the charts
def landing_view(request):
    """Renders the landing page"""
    return render(request, 'landing.html')


@login_required(login_url="accounts:login")
def home(request):
    """Renders the home page"""
    return render(request, 'dashboard.html')


@login_required(login_url="accounts:login")
def lead_source_view(request):
    """Renders the lead source list page"""
    context = {}

    # Add the list of lead sources
    context['lead_sources'] = LeadSources.objects.filter(user=request.user)

    return render(request, 'call_tracking/leadsource.html', context)

@login_required(login_url="accounts:login")
def phone_numbers_view(request):
    """Renders the phone numbers list page"""
    context = {}

    # Add the area code form - default to 415
    context['form'] = AreaCodeForm({'area_code': None})

    # Add the list of lead sources
    context['PurchasedNumbers'] = PurchasedNumbers.objects.filter(user=request.user)

    return render(request, 'phone_numbers.html', context)


class AddExistingNumber(CreateView):
    model = PurchasedNumbers
    template_name = 'call_tracking/addexistingnumber_form.html'
    fields = ['phone_number']

    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        # do something with self.object
        self.object.user = self.request.user
        self.object.save()
        return HttpResponseRedirect(reverse('call_tracking:phone_numbers'))
    


@login_required(login_url="accounts:login")
def leads_by_source(request):
    """Returns JSON data about the lead sources and how many leads they have"""
    # Invoke a LeadSource classmethod to get the data
    data = LeadSources.objects.get_leads_per_source(request.user)

    # Return it as JSON - use safe=False because we're sending a JSON array
    return JsonResponse(data, safe=False)


@login_required(login_url="accounts:login")
def leads_by_city(request):
    """Returns JSON data about the different cities leads come from"""
    # Invoke a Lead classmethod to get the data
    data = Lead.objects.get_leads_per_city(request.user)

    # Return it as JSON - use safe=False because we're sending a JSON array
    return JsonResponse(data, safe=False)


def leads_by_zipcode(request):
    """Returns JSON data about callers' zipcodes"""
    # Invoke a Lead classmethod to get the data
    data = Lead.objects.get_leads_per_zipcode(request.user)

    # Return it as JSON - use safe=False because we're sending a JSON array
    return JsonResponse(data, safe=False)


# Views for purchase number workflow
@login_required(login_url="accounts:login")
def available_numbers(request):
    """Uses the Twilio API to generate a list of available phone numbers"""
    form = AreaCodeForm(request.POST)

    if form.is_valid():
        # We received a valid area code - query the Twilio API
        area_code = form.cleaned_data['area_code']

        available_numbers = search_phone_numbers(area_code=area_code)

        # Check if there are no numbers available in this area code
        if not available_numbers:
            messages.error(
                request,
                'There are no Twilio numbers available for area code {0}. Search for numbers in a different area code.'.format(area_code))
            return redirect('call_tracking:home')

        context = {}
        context['available_numbers'] = available_numbers

        return render(request, 'call_tracking/available_numbers.html', context)
    else:
        # Our area code was invalid - flash a message and redirect back home
        bad_area_code = form.data['area_code']
        messages.error(request, '{0} is not a valid area code. Please search again.'
                       .format(bad_area_code))

        return redirect('call_tracking:home')

@login_required(login_url="accounts:login")
def purchase_number(request):
    """Purchases a new phone number using the Twilio API"""
    form = PurchaseNumberForm(request.POST)

    if form.is_valid():
        # Purchase the phone number
        phone_number = form.cleaned_data['phone_number']
        twilio_number = purchase_phone_number(phone_number.as_e164)

        # Save it in a new PurchasedNumbers object
        purchased_number = PurchasedNumbers(user=request.user, phone_number=twilio_number.phone_number)
        purchased_number.save()

        # Save it in a new LeadSource object
        lead_source = LeadSources(incoming_number=twilio_number.phone_number)
        lead_source.save()

        messages.success(
            request,
            'Phone number {0} has been purchased. Please add a name for this lead source.'.format(
                twilio_number.friendly_name))

        # Redirect to edit lead page
        return redirect('call_tracking:edit_lead_source', pk=lead_source.pk)
    else:
        # In the unlikely event of an error, redirect to the home page
        bad_phone_number = form.data['phone_number']
        messages.error(request, '{0} is not a valid phone number. Please search again.'
                       .format(bad_phone_number))

        return redirect('call_tracking:list_numbers')

@login_required(login_url="accounts:login")
def campaigns(request):
    """Renders the campaign list page"""
    context = {}

    # Add the list of campaigns
    context['campaigns'] = Campaign.objects.filter(user=request.user)

    return render(request, 'call_tracking/campaigns.html', context)

def new_campaign(request):
    """Powers a form to edit Campaigns"""
    
     # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CampaignForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            obj = form.save(commit=False)
            messages.success(request, 'Campaign successfully created.')
            obj.user = request.user
            obj.save()
            form.save_m2m()
            # redirect to a new URL:
            return redirect('call_tracking:campaigns')
        else:
            messages.error(request, 'not a valid field. Please try again.')
            return redirect('call_tracking:campaigns')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = CampaignForm()

    return render(request, 'call_tracking/new_campaign.html', {'form': form})

class CampaignUpdateView(SuccessMessageMixin, UpdateView):
    """Powers a form to edit Lead Sources"""
    model = Campaign
    fields = ['name', 'channel', 'lead_sources']
    success_url = reverse_lazy('call_tracking:campaigns')
    success_message = 'Campaign successfully updated.'

def newleadsource(request):
    """Powers a form to edit Lead Sources"""
    
     # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = LeadSourceForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            obj = form.save(commit=False)
            messages.success(request, 'Lead source successfully created.')
            obj.user = request.user
            obj.save()
            # redirect to a new URL:
            return redirect('call_tracking:lead_sources')
        else:
            messages.error(request, 'not a valid field. Please try again.')
            return redirect('call_tracking:lead_sources')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = LeadSourceForm()

    return render(request, 'call_tracking/new_lead_source.html', {'form': form})

class LeadSourceUpdateView(SuccessMessageMixin, UpdateView):
    """Powers a form to edit Lead Sources"""
    model = LeadSources
    fields = ['name', 'forwarding_number']
    success_url = reverse_lazy('call_tracking:lead_sources')
    success_message = 'Lead source successfully updated.'

class CallAudioView(DetailView):
    """Let's user play any call recording audio"""

    model = Call
    fields = ['lead_number', 'start_timestamp', 'source_number', 'lead_source']
    success_url = reverse_lazy('call_tracking:lead_sources')

    # return render(request, 'vuetemplates/call_audio.html')

class CallInfoView(DetailView):
    """Powers a form to edit Lead Sources"""

    model = Call
    fields = ['lead_number', 'start_timestamp', 'source_number', 'lead_source']


# View used by Twilio API to connect callers to the right forwarding
# number for that lead source
@csrf_exempt
def forward_call(request):
    """Connects an incoming call to the correct forwarding number"""
    # First look up the lead source
    source = LeadSources.objects.get(incoming_number=request.POST['Called'])
    # Then look up the lead's user
    user = source.user

    # Create a lead entry for this call
    lead = Lead(
        user=user,
        source=source,
        phone_number=request.POST['Caller'],
        city=request.POST['CallerCity'],
        state=request.POST['CallerState'],
        zipcode=request.POST['CallerZip'],
    )

    lead.save()

    # Immediately create a recent call entry
    call = Call(
        user=user,
        lead_number = request.POST['Caller'],
        lead_source = source,
        forwarding_number = getattr(source, 'forwarding_number')
     )

    call.save()

    # Respond with some TwiML that connects the caller to the forwarding_number
    response = VoiceResponse()
    response.record()
    response.dial(source.forwarding_number.as_e164)

    
    return HttpResponse(response)


def VueCallsList(request):
    """Renders the calls page"""
    context = {}

    # Add the list of lead sources
    calls = Call.objects.filter(user=request.user)
    context["calls_json"] = serialize('json', calls)

    return render(request, 'vuetemplates/vuecalls.html', context)


class CallsList(ListView):
    model = Call
    template_name = 'recentactivity.html'
    context_object_name = 'calls'
    #Before I overrode the get_queryset method, this is what I used and it return all call objects because I didn't sort by user
    # queryset = Call.objects.order_by('-start_timestamp')
    paginate_by = 10
    
    def get_queryset(self):
        return Call.objects.filter(user=self.request.user).order_by('-start_timestamp')


def caller_info_view(number):
    print(number)

    return JsonResponse({'callerinfo': number})

def get_token(request):
    """Returns a Twilio Client token"""
    # Create a TwilioCapability token with our Twilio API credentials
    capability = ClientCapabilityToken(
        settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN
    )

    # Allow our users to make outgoing calls with Twilio Client
    capability.allow_client_outgoing(settings.TWIML_APP_SID_BROWSERCALL)

    # If the user is on the support dashboard page, we allow them to accept
    # incoming calls to "sales_rep"
    # (in a real app we would also require the user to be authenticated)
    if request.GET['forPage'] == reverse('call_tracking:recent-activity'):
        capability.allow_client_incoming('sales_rep')
    else:
        # Otherwise we give them a name of "lead"
        capability.allow_client_incoming('lead')

    # Generate the capability token
    token = capability.to_jwt()

    return JsonResponse({'token': token.decode('utf-8')})


@csrf_exempt
def call(request):
    """Returns TwiML instructions to Twilio's POST requests"""
    response = VoiceResponse()
    dial = response.dial(caller_id='+12055962900')
    #restclient = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    

    # If the browser sends this view a clientphoneNumber param in the request, we know a support agent is trying to call a customer
    if 'clientphoneNumber' in request.POST:
        # print(request.POST)
        # print("leadNumber: " + request.POST['clientphoneNumber'])
        # print("leadID: " + request.POST['leadID'])
        dial.number(
             request.POST['clientphoneNumber'],
             status_callback_event='initiated ringing answered completed',
             status_callback='https://callme.ngrok.io/twl/callback')
        response.record(recording_status_callback_event='in-progress completed absent', recording_status_callback='https://callme.ngrok.io/twl/callback')
        #newcall = restclient.calls.create(twiml='<Response><Say>Ahoy, World!</Say></Response>',to=request.POST['clientphoneNumber'], from_='+12055962900')
        lead = Call.objects.get(id=request.POST['leadID'])
         # Then look up the lead's user
        user = lead.user
        # Immediately create a recent call entry
        call = Call(
            user=user,
            lead_number = request.POST['clientphoneNumber'],
            in_browser = True,
            inbound = False,
        )

        call.save()

        print(response)
   
        # """elif user.userstatus == forward"""
        return HttpResponse(str(response), content_type='application/xml; charset=utf-8')
        #print(newcall.sid)
        #return HttpResponse(content_type='', status=200)
       
    elif 'outNumber' in request.POST:
        dial.number(
             request.POST['outNumber'],
             status_callback_event='initiated ringing answered completed',
             status_callback='https://callme.ngrok.io/twl/callback')
        response.record(recording_status_callback_event='in-progress completed absent', recording_status_callback='https://callme.ngrok.io/twl/callback')
        
        user = User.objects.get(username=request.POST['user'])
        # Immediately create a recent call entry
        call = Call(
            user=user,
            lead_number = request.POST['outNumber'],
            in_browser = True,
            inbound = False,
        )

        call.save()

        print(response)
   
        # """elif user.userstatus == forward"""
        return HttpResponse(str(response), content_type='application/xml; charset=utf-8')

    else:
        # Otherwise we assume this request is a lead trying
        # to contact support
        #response.play('https://ymstat.com/dyn/community/52797.mp3', loop=1)
        dial.client('sales_rep')
        #Pass the Skip trace view function caller's number
        # caller_info_view(request.POST['Caller'])
        source = LeadSources.objects.get(incoming_number=request.POST['Called'])
        # Then look up the lead's user
        user = source.user

        # Create a lead entry for this call
        lead = Lead(
            user=user,
            source=source,
            phone_number=request.POST['Caller'],
            city=request.POST['CallerCity'],
            state=request.POST['CallerState'],
            zipcode=request.POST['CallerZip'],
        )

        lead.save()

        # Immediately create a recent call entry
        call = Call(
            user=user,
            lead_number = request.POST['Caller'],
            lead_source = source,
            forwarding_number = getattr(source, 'forwarding_number'),
            in_browser = True,
            inbound = True,
        )

        call.save()
        
        response.record()

        return HttpResponse(
            str(response), content_type='application/xml; charset=utf-8'
        )


@csrf_exempt
def call_status_callback(request):
    print(request.POST)
    return HttpResponse(content_type='', status=204)