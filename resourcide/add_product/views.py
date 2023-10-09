from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.shortcuts import render, redirect, get_object_or_404  # Import render and redirect.
from django.db import transaction, IntegrityError
from django.contrib import messages
from django.urls import reverse
from multiupload.fields import MultiFileField
from .forms import NameForm, DescriptionForm, PhotoUploadForm
from .models import Product, ProductImage

def first_step(request):
    if request.method == 'POST':
        form = NameForm(request.POST)
        if form.is_valid():
            # Save the product name to the database.
            try:
                product = Product(name=form.cleaned_data['name'])
                product.save()

                # Store the product_id in the session
                request.session['product_id'] = product.id

                messages.success(request, 'Product name saved successfully.')
                # Redirect to the second page.
                return redirect('second_step')
            except:
                print('fail')
    else:
        form = NameForm()

    return render(request, 'step1.html', {'form': form})
    # templates = loader.get_template('step1.html')
    # return HttpResponse(templates.render())

def second_step(request):
    # Retrieve the product_id from the session
    product_id = request.session.get('product_id')

    # Check if the product_id exists in the session
    if not product_id:
        return redirect('first_step')  # Redirect to step 1 if the product_id is not in the session

    product = Product.objects.get(id=product_id)

    if request.method == 'POST':
        form = DescriptionForm(request.POST)
        if form.is_valid():
            # Get the product from the database using the retrieved product_id
            product.description = form.cleaned_data['description']
            product.save()
            
            # Redirect to 'third_step' with the product_id parameter
            return redirect(reverse('third_step', kwargs={'product_id': product_id}))
    
    else:
        form = DescriptionForm()

    product_id = request.session.get('product_id')
    product = Product.objects.get(id=product_id)

    return render(request, 'step2.html', {'form': form, 'product_name': product.name})


def third_step(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'POST':
        form = PhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Handle multiple image uploads
            images = request.FILES.getlist('images')
            uploaded_images = []

            try:
                with transaction.atomic():
                    for image in images:
                        # Create a ProductImage object associated with the product
                        product_image = ProductImage(product=product, image=image)
                        product_image.save()

                        # Append the image URL to the list for preview
                        uploaded_images.append(product_image.image.url)

            except IntegrityError:
                # Handle any IntegrityError, such as the NOT NULL constraint failure
                pass
            # return redirect(reverse('fourth_step', kwargs={'product_id': product_id}))
    else:
        form = PhotoUploadForm()

    return render(request, 'step3.html', {'form': form, 'product_name': product.name, 'product_id': product_id})


def fourth_step(request, product_id):
    
    product = get_object_or_404(Product, pk=product_id)

    return render(request, 'step4.html', {'product_name': product.name, 'product_id': product_id, 'product_des': product.description})
    # templates = loader.get_template('step4.html')
    # return HttpResponse(templates.render())

# def check_product(request):
#     # Retrieve the latest saved product from the database.
#     try:
#         latest_product = Product.objects.latest('id')  # Assuming 'id' is the primary key.
#         product_name = latest_product.name
#     except Product.DoesNotExist:
#         product_name = "No product found."

#     return render(request, 'check_product.html', {'product_name': product_name})
