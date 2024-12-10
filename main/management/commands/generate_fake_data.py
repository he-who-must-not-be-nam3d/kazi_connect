from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from main.models import JobListing, UserProfile
from faker import Faker
import random

class Command(BaseCommand):
    help = 'Generate mock data for the application with relevant skills'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Predefined job titles and relevant skills
        job_skills = {
            "Software Engineer": ["Python", "Django", "SQL", "JavaScript", "REST APIs"],
            "Data Scientist": ["Python", "Machine Learning", "Data Analysis", "R", "SQL"],
            "Graphic Designer": ["Adobe Photoshop", "Illustrator", "UI/UX Design", "Creativity"],
            "Marketing Specialist": ["SEO", "Content Creation", "Google Analytics", "Social Media"],
            "Project Manager": ["Agile Methodologies", "Communication", "Team Leadership", "Budgeting"],
            "Accountant": ["Financial Analysis", "Excel", "QuickBooks", "Tax Preparation"],
            "HR Manager": ["Recruitment", "Employee Relations", "Payroll", "Compliance"],
        }

        # Create 5 admin users
        # for i in range(5):
        #     username = f"admin{i+1}"
        #     email = f"{username}@example.com"
        #     user, created = User.objects.get_or_create(
        #         username=username,
        #         defaults={
        #             'email': email,
        #             'is_staff': True,
        #             'is_superuser': True,
        #         }
        #     )
        #     if created:
        #         user.set_password('password123')  # Set a default password
        #         user.save()
        #         self.stdout.write(f"Created admin user: {username}")
        #
        #     # Create 5 job listings for each admin
        #     for _ in range(5):
        #         title = random.choice(list(job_skills.keys()))
        #         skills = random.sample(job_skills[title], 3)  # Randomly select 3 skills for the job
        #         JobListing.objects.create(
        #             title=title,
        #             description=fake.text(max_nb_chars=200),
        #             company_name=fake.company(),
        #             location=fake.city(),
        #             employment_type=random.choice(['Full-time', 'Part-time']),
        #             company_logo=None,
        #             skills=', '.join(skills),
        #             employer=user,
        #         )
        #     self.stdout.write(f"Created 5 job listings for admin user: {username}")

        # self.stdout.write(self.style.SUCCESS("Mock data generation complete!"))

        for i in range(3):  # 3 job seekers
            job_seeker = User.objects.create_user(
                username=f"jobseeker{i + 1}",
                password="password",
                email=f"jobseeker{i + 1}@example.com",
                first_name=f"JobSeeker{i + 1}",
                last_name="User"
            )
            UserProfile.objects.create(user=job_seeker, user_type="job_seeker")
            job_seeker_profile = UserProfile.objects.get(user=job_seeker)
            seeker_skills = ", ".join(random.sample(skills_pool, k=5))  # Random skills
            print(f"Job Seeker {job_seeker.username} Skills: {seeker_skills}")

        self.stdout.write(self.style.SUCCESS("Mock data generated successfully!"))