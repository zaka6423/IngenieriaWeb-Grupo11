# context_processors.py
from django.contrib.auth.models import User
from .models import UserProfile

def email_verification_status(request):
    """
    Context processor para incluir el estado de verificación del email en todos los templates
    """
    context = {}
    
    if request.user.is_authenticated:
        try:
            profile = request.user.userprofile
            context['email_verified'] = profile.email_verified
        except UserProfile.DoesNotExist:
            context['email_verified'] = False
    else:
        context['email_verified'] = False
    
    return context
