from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile, CustomerAddress, ProfileForm, CustomerAddressForm

@login_required
def profile_view(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    address = profile.address
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        address_form = CustomerAddressForm(request.POST, instance=address)
        if profile_form.is_valid() and address_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            address = address_form.save(commit=False)
            address.user = user
            address.save()
            profile.address = address
            profile.save()
            messages.success(request, "Profile and address updated successfully!")
            return redirect('profile')
    else:
        profile_form = ProfileForm(instance=profile)
        address_form = CustomerAddressForm(instance=address)

    return render(request, 'customer/profile.html', {'profile_form': profile_form, 'address_form': address_form, 'profile': profile, 'user': user,})