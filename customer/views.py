from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile, CustomerAddress, ProfileForm, CustomerAddressForm
from products .models import ProductHistory

@login_required
def profile_view(request):
    user = request.user
    print(f"DEBUG: Logged in user email = {user.email}")
    profile, created = Profile.objects.get_or_create(user=user, defaults={'email': user.email or ''})
    if user.email and profile.email != user.email:
        profile.email = user.email
        profile.save()
    address_instance = profile.address if hasattr(profile, 'address') else None
    address_form = CustomerAddressForm(instance=address_instance)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        address_form = CustomerAddressForm(request.POST, instance=address_instance)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.save()
        if address_form.is_valid():
            address = address_form.save(commit=False)
            address.user = user
            address.save()
            if not hasattr(profile, 'address') or profile.address != address:
                profile.address = address
                profile.save()
        return redirect('home')
    else:
        form = ProfileForm(instance=profile)
    history = ProductHistory.objects.filter(user=user).order_by('-purchased_at')
    return render(request, 'profile.html', {'form': form, 'profile': profile, 'user': user, 'history': history, 'address_form': address_form})