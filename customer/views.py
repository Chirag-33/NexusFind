from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile, ProfileForm, CustomerAddressForm
from checkout.models import Order

@login_required
def profile_view(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)
    address_instance = profile.address if hasattr(profile, 'address') else None
    editing = request.GET.get('edit') == '1' or request.method == 'POST'

    if request.method == 'POST':
        if request.GET.get('remove_picture') == '1':
            profile.profile_picture.delete()
            profile.profile_picture = None
            profile.save()
            form_data = {'email': request.POST.get('email', profile.email), 'phone_number': request.POST.get('phone_number', profile.phone_number),}
            address_form_data = {'address_line_1': request.POST.get('address_line_1', address_instance.address_line_1 if address_instance else ''), 'address_line_2': request.POST.get('address_line_2', address_instance.address_line_2 if address_instance else ''), 'address_type': request.POST.get('address_type', address_instance.address_type if address_instance else ''), 'city': request.POST.get('city', address_instance.city if address_instance else ''), 'state': request.POST.get('state', address_instance.state if address_instance else ''), 'country': request.POST.get('country', address_instance.country if address_instance else ''), 'pincode': request.POST.get('pincode', address_instance.pincode if address_instance else ''),}
            form = ProfileForm(form_data, instance=profile)
            address_form = CustomerAddressForm(address_form_data, instance=address_instance)
            user.username = request.POST.get('username', user.username)
        else:
            form = ProfileForm(request.POST, request.FILES, instance=profile)
            address_form = CustomerAddressForm(request.POST, instance=address_instance)
            if form.is_valid() and address_form.is_valid():
                new_username = request.POST.get('username')
                if new_username and new_username != user.username:
                    user.username = new_username
                    user.save()
                profile = form.save()
                address = address_form.save(commit=False)
                address.user = user
                address.save()
                profile.address = address
                profile.save()
                return redirect('profile')
            else:
                user.username = request.POST.get('username', user.username)
    else:
        form = ProfileForm(instance=profile)
        address_form = CustomerAddressForm(instance=address_instance)

    history = Order.objects.filter(user=user).prefetch_related('items__product').order_by('-created_at')
    return render(request, 'profile.html', {'user': user, 'profile': profile, 'form': form, 'address_form': address_form, 'history': history, 'editing': editing})