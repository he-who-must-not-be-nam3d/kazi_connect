from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.
class JobListing(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    company_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    employment_type = models.CharField(max_length=50, choices=[('Full-time', 'Full-time'), ('Part-time', 'Part-time')])
    company_logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    skills = models.TextField(help_text="Comma-separated list of skills (e.g., Python, Django, SQL)", default='web developer')
    employer = models.ForeignKey(User, on_delete=models.CASCADE, default='1')

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('job_seeker', 'Job Seeker'),
        ('employer', 'Employer'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.user_type}"


class JobSeekerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    skills = models.TextField(blank=True, help_text="Comma-separated list of skills")

    def __str__(self):
        return f"{self.user.username}'s Profile"

class JobApplication(models.Model):
    job = models.ForeignKey('JobListing', on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=20,
                              choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
                              default='pending')
    cover_letter = models.TextField()
    cv = models.FileField(upload_to='cvs/')
    applied_at = models.DateTimeField(auto_now_add=True)
    last_status_update = models.DateTimeField(auto_now=True)

    def status_changed(self):
        return self.last_status_update > self.applied_at

    def __str__(self):
        return f"{self.full_name} ({self.email}) - {self.job.title}"


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        JobSeekerProfile.objects.create(user=instance)
