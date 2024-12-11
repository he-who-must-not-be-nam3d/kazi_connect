from django.core.management.base import BaseCommand
from main.models import JobListing
from faker import Faker
from PIL import Image, ImageDraw, ImageFont
import os
from io import BytesIO
from django.db.models import Q


class Command(BaseCommand):
    help = "Generate fake company logos for job listings without logos"

    def handle(self, *args, **kwargs):
        fake = Faker()
        save_dir = "media/company_logo/"
        os.makedirs(save_dir, exist_ok=True)

        # Find all job listings without logos (NULL or empty string)
        job_listings = JobListing.objects.filter(Q(company_logo__isnull=True) | Q(company_logo=""))

        if job_listings.exists():
            for job in job_listings:
                company_name = job.company_name

                # Generate a random logo
                image = Image.new("RGB", (150, 150), color=fake.color())
                draw = ImageDraw.Draw(image)

                # Use PIL's default font or a custom one
                font = ImageFont.load_default()

                # Get text width and height to center it
                text = company_name[:2].upper()  # Use first two letters of company name
                text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:]

                # Position the text at the center
                text_position = ((150 - text_width) // 2, (150 - text_height) // 2)

                # Add company initials or name
                draw.text(text_position, text, font=font, fill="white")

                # Save the logo to the file system
                file_path = os.path.join(save_dir, f"{company_name}.png")
                image.save(file_path)

                # Update the job listing with the logo file path
                job.company_logo = f"company_logo/{company_name}.png"
                job.save()

                print(f"Saved logo for {company_name}: {file_path}")
        else:
            print("No job listings found without logos.")
