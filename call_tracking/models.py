from django.db import models
from django.conf import settings
from django.db.models import Count
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User


class Campaign(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, default=None, null=True)
    name = models.CharField(
        max_length=100, null=True)
    MARKETING_CHANNELS = (
        ('Bandit', 'Bandit Sign'),
        ('Web', 'Online'),
        ('Mail', 'Direct Mail')
    )
    channel = models.CharField(
        max_length=50,
        choices=MARKETING_CHANNELS,
        blank=False, default='Bandit',
        verbose_name='Marketing Channel' )
    lead_sources = models.ManyToManyField(
        'LeadSources')

class CampaignManager(models.Manager):
    """A custom manager which adds a 'get_campaigns_per_user' method"""

    def get_campaigns_per_user(self, user):
        """Get the number of calls for each campaign"""
        # Use Django's annotate feature to include the number of calls
        # on each campaign
        queryset = self.filter(user=user).annotate(
            Count('call')).order_by('timestamp')

        # Extract the lead numbers and call counts and make them a regular list
        data = list(queryset.values('leadnumber', 'call__count'))

        return data

class LeadSourcesManager(models.Manager):
    """A custom manager which adds a 'get_leads_per_source' method"""

    def get_leads_per_source(self, user):
        """Get the number of leads for each lead source"""
        # Use Django's annotate feature to include the number of leads
        # on each lead source
        queryset = self.filter(user=user).annotate(
            Count('lead')).order_by('name')

        # Extract the source names and lead counts and make them a regular list
        data = list(queryset.values('name', 'lead__count'))

        return data


class LeadSources(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, default=None, null=True)
    name = models.CharField(
        max_length=100,
        blank=True,
        help_text='It helps to be specific for easy attribution. E.g. "Bandit sign @ i20 exit 31"')
    incoming_number = PhoneNumberField(
        blank=True, null=True,
        help_text='A phone number purchased through Twilio')
    forwarding_number = PhoneNumberField(
        blank=True,
        help_text='People who call this lead source will be connected with this phone number. Must include international prefix - e.g. +1 555 555 5555')

    # Apply our custom manager
    objects = LeadSourcesManager()

    def __str__(self):
        if self.name:
            return '{0} - {1}'.format(self.name, self.incoming_number)
        else:
            return 'unnamed lead source - {0}'.format(self.incoming_number)


class LeadManager(models.Manager):
    """A custom manager which adds a 'get_leads_per_city' method"""

    def get_leads_per_city(self, user):
        """Get the number of leads for each city"""
        # Use Django's annotate feature to include the number of leads
        # from each distinct city
        queryset = self.filter(user=user).values('city').annotate(
            Count('id')).order_by('city')

        # Extract the cities and lead counts and make them a regular list
        data = list(queryset.values('city', 'id__count'))

        return data

    def get_leads_per_zipcode(self, user):
        """Get the number of leads for each zip code"""
        # Use Django's annotate feature to include the number of leads
        # from each distinct city
        queryset = self.filter(user=user).values('zipcode').annotate(
            Count('id')).order_by('zipcode')

        # Extract the cities and lead counts and make them a regular list
        data = list(queryset.values('zipcode', 'id__count'))

        return data


class Lead(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    source = models.ForeignKey(LeadSources, on_delete=models.CASCADE)
    phone_number = PhoneNumberField()
    timestamp = models.DateTimeField(auto_now_add=True)

    # A couple examples of fields you could track for each incoming call
    # See https://www.twilio.com/docs/api/twiml/twilio_request for more
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    zipcode = models.CharField(default='No zipcode', max_length=10)

    # Apply our custom manager
    objects = LeadManager()

    def __str__(self):
        return '{4}- {0}, {1} {3} at {2}'.format(self.city, self.state, self.timestamp, self.zipcode, self.user)


class CallManager(models.Manager):
    """A custom manager which adds a 'get_calls_per_user' method"""

    def get_calls_per_user(self, user):
        """Get the number of calls for each lead source"""
        # Use Django's annotate feature to include the number of calls
        # on each lead source
        queryset = self.filter(user=user).annotate(
            Count('call')).order_by('timestamp')

        # Extract the lead numbers and call counts and make them a regular list
        data = list(queryset.values('leadnumber', 'call__count'))

        return data


class Call(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lead_number = PhoneNumberField(blank=True)
    inbound = models.BooleanField(default=True)
    in_browser = models.BooleanField(default=False)
    start_timestamp = models.DateTimeField(auto_now_add=True)
    end_timestamp = models.DateTimeField(auto_now=True)
    source_number = PhoneNumberField(blank=True)
    lead_source = models.ForeignKey(LeadSources, on_delete=models.CASCADE, default=1)
    forwarding_number = PhoneNumberField(blank=True)
    # Apply our custom manager
    objects = CallManager()

    def __str__(self):
        return '{1}- at {0}'.format(self.start_timestamp, self.user)


class PurchasedNumbers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = PhoneNumberField(blank=True)


class UsersPhoneNumbers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)