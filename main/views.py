import re

from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from main.forms import JobListingForm, RegistrationForm, SkillsInputForm, JobApplicationForm
from main.models import JobListing, JobSeekerProfile, JobApplication, UserProfile


# Create your views here.
def home(request):
    job_list = JobListing.objects.all().order_by('-id')  # Fetch jobs in descending order of ID
    paginator = Paginator(job_list, 9)  # 9 items per page
    page_number = request.GET.get('page')
    jobs = paginator.get_page(page_number)
    return render(request, 'home.html', {'jobs': jobs})


@login_required
def dashboard(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)

        # Check if the user is a job seeker
        if user_profile.user_type == 'job_seeker':
            # Fetch the JobSeekerProfile instance
            try:
                job_seeker_profile = JobSeekerProfile.objects.get(user=request.user)
                job_seeker_skills = job_seeker_profile.skills

                if job_seeker_skills:
                    # Parse and normalize skills
                    skill_list = [
                        skill.strip().lower()
                        for skill in job_seeker_skills.split(',')
                        if skill.strip()
                    ]

                    # Query matching job listings using robust regex
                    job_listings = JobListing.objects.filter(
                        Q(skills__iregex=r'\b(?:' + '|'.join(map(re.escape, skill_list)) + r')\b')
                    ).distinct()

                    print(f"Number of matching job listings: {job_listings.count()}")

                    # Add match percentage calculation
                    for job in job_listings:
                        matched_skills = [
                            skill for skill in skill_list if skill.lower() in job.skills.lower()
                        ]
                        job.match_percentage = (len(matched_skills) / len(skill_list)) * 100 if skill_list else 0

                    # Sort by match percentage
                    job_listings = sorted(
                        job_listings,
                        key=lambda x: getattr(x, 'match_percentage', 0),
                        reverse=True
                    )
                else:
                    print("No skills found for the job seeker")
                    job_listings = JobListing.objects.none()
            except JobSeekerProfile.DoesNotExist:
                print("No JobSeekerProfile found for the user")
                job_listings = JobListing.objects.none()
        else:
            # For employers or other user types
            job_listings = JobListing.objects.all()

        return render(request, 'dashboard.html', {
            'job_listings': job_listings,
            'user': request.user,
            'profile': user_profile,
        })

    except UserProfile.DoesNotExist:
        print("UserProfile does not exist")
        return render(request, 'dashboard.html', {
            'job_listings': JobListing.objects.all(),
            'user': request.user,
            'profile': None,
        })


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Create User
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Determine user type and create UserProfile
            user_type = form.cleaned_data['user_type']
            user_profile = UserProfile.objects.create(user=user, user_type=user_type)

            # Login the user
            login(request, user)

            # Redirect based on user type
            if user_type == 'job_seeker':
                return redirect('skills_input', user_id=user.id)
            elif user_type == 'employer':
                return redirect('dashboard')
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})


def skills_input(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = SkillsInputForm(request.POST)
        if form.is_valid():
            skills = form.cleaned_data['skills']

            # Check if the user already has a profile, or create one
            profile, created = JobSeekerProfile.objects.get_or_create(user=user)
            profile.skills = skills
            profile.save()

            return HttpResponseRedirect(reverse('dashboard'))  # Redirect to the dashboard after saving
    else:
        form = SkillsInputForm()

    return render(request, 'skills_input.html', {'form': form})


@login_required
def create(request):
    if request.method == 'POST':
        form = JobListingForm(request.POST, request.FILES)
        if form.is_valid():
            job_listing = form.save(commit=False)
            job_listing.employer = request.user
            job_listing.save()
            messages.success(request, 'Job listing created successfully!')
            return redirect('dashboard')
    else:
        form = JobListingForm()

    return render(request, 'listings/create.html', {'form': form})


@login_required
def manage(request, id):
    # Fetch the job listing that matches the id and belongs to the logged-in employer
    job = get_object_or_404(JobListing, id=id, employer=request.user)

    if request.method == 'POST':
        # Process the form submission
        form = JobListingForm(request.POST, request.FILES, instance=job)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # Redirect to the employer's dashboard
    else:
        # Pre-fill the form with existing job data
        form = JobListingForm(instance=job)

    return render(request, 'manage_listing.html', {'form': form, 'job': job})


@login_required
def apply(request, job_id):
    job = get_object_or_404(JobListing, id=job_id)

    if hasattr(request.user, 'profile'):  # Assuming job seekers have a profile
        if request.method == 'POST':
            form = JobApplicationForm(request.POST, request.FILES)
            if form.is_valid():
                # Save the application
                JobApplication.objects.create(
                    job=job,
                    applicant=request.user,
                    full_name=form.cleaned_data['full_name'],
                    email=form.cleaned_data['email'],
                    phone_number=form.cleaned_data['phone_number'],
                    location=form.cleaned_data['location'],
                    cover_letter=form.cleaned_data['cover_letter'],
                    cv=form.cleaned_data['cv']
                )
                messages.success(request, "Your application has been submitted successfully!")
                return redirect('dashboard')
        else:
            form = JobApplicationForm()

        return render(request, 'apply.html', {'job': job, 'form': form})
    else:
        messages.error(request, "You must be a job seeker to apply for a job.")
        return redirect('home')


@login_required
def applications(request):
    user_profile = UserProfile.objects.get(user=request.user)

    if user_profile.user_type == 'employer':
        # Fetch applications for the employer's job listings
        job_listings = JobListing.objects.filter(employer=request.user)
        applications = JobApplication.objects.filter(job__in=job_listings)
    else:  # job_seeker
        # Fetch applications made by the logged-in user
        applications = JobApplication.objects.filter(applicant=request.user)

    if request.method == 'POST' and user_profile.user_type == 'employer':
        # Handle status update
        application_id = request.POST.get('application_id')
        new_status = request.POST.get('status')
        application = JobApplication.objects.get(id=application_id)
        application.status = new_status
        application.save()
        return redirect('applications')

    return render(request, 'applications.html', {'applications': applications, 'user_profile': user_profile})


@login_required
def details(request, job_id):
    # Fetch the job listing
    job = get_object_or_404(JobListing, id=job_id)

    # Determine the user type and ownership of the listing
    user = request.user
    is_employer = hasattr(user, 'joblisting_set')  # Check if the user has job listings (employer)
    is_job_seeker = hasattr(user, 'profile')  # Check if the user has a profile (job seeker)
    owns_listing = job.employer == user if is_employer else False

    context = {
        'job': job,
        'is_job_seeker': is_job_seeker,
        'is_employer': is_employer,
        'owns_listing': owns_listing,
    }

    return render(request, 'listings/listing_details.html', context)


@login_required
def delete_listing(request):
    return None


def login_user(request):
    if request.method == "GET":
        return render(request, 'login.html')
    elif request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, 'You are now Logged In!')
            return redirect("dashboard")
        messages.warning(request, "Invalid Username or Password Combo")
        return redirect("login")


def logout_user(request):
    logout(request)
    messages.success(request, "You are logged out successfully")
    return redirect('home')


@login_required
def update_status(request):
    if request.method == 'POST':
        application_id = request.POST.get('application_id')
        new_status = request.POST.get('status')

        print(f"Received application_id: {application_id}, new_status: {new_status}")
        application = get_object_or_404(JobApplication, id=application_id)

        if application.job.employer == request.user:
            # Update the status and save
            application.status = new_status
            application.save()

            # Add a message to confirm success (optional)
            messages.success(request, "Application status updated successfully.")

            return redirect('applications')
        else:
            # If the employer doesn't match the user, return an error
            messages.error(request, "You are not authorized to update this application status.")
            return redirect('applications')  # Redirect back to the applications page


        return redirect('applications')
