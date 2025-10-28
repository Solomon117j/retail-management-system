from django.core.management.base import BaseCommand
from procurement.models import Supplier

class Command(BaseCommand):
    help = 'Populate suppliers with provided data'

    def handle(self, *args, **options):
        suppliers_data = [
            {
                'name': 'Dis-Chem Direct',
                'industry': 'National Distributor',
                'notes': 'Wholesale division of major pharmacy chain; supplies businesses nationwide. Key Products: Nitrile, Latex, Vinyl exam & surgical gloves. Contact Info: (Search website for regional sales contacts)',
                'website': 'https://dischemdirect.co.za',
            },
            {
                'name': 'Lohmann & Rauscher',
                'industry': 'National Distributor',
                'notes': 'International manufacturer & supplier of high-quality surgical/medical products. Key Products: Surgical & Examination Gloves. Contact Info: (Find contact form or phone number on site)',
                'website': 'https://lohmann-rauscher.co.za',
            },
            {
                'name': 'BD (Becton Dickinson) SA',
                'industry': 'National Distributor',
                'notes': 'Global medical tech company; supplier of specialized surgical gloves. Key Products: Surgical Gloves. Contact Info: (Use website\'s "Contact Us" section)',
                'website': 'https://bd.com/en-za',
            },
            {
                'name': 'Amayeza Abantu',
                'industry': 'Medical Supplier',
                'notes': 'Significant supplier of pharmaceuticals and medical sundries. Key Products: Exam & Surgical Gloves. Contact Info: (Locate contact details on their site)',
                'website': 'https://amayeza-abantu.co.za',
            },
            {
                'name': 'BLS Systems',
                'industry': 'PPE Supplier',
                'notes': 'Major international manufacturer of PPE, including gloves. Key Products: Nitrile, Latex Gloves. Contact Info: (Find local SA distributor via website)',
                'website': 'https://bls-systems.com',
            },
            {
                'name': 'UMS Group',
                'industry': 'PPE Supplier',
                'notes': 'Leading supplier of industrial & safety equipment, including gloves. Key Products: Industrial & Medical-Grade Gloves. Contact Info: (Check for a medical/PPE division contact)',
                'website': 'https://umsgroup.co.za',
            },
            {
                'name': 'Bridgestone SA (Industrial)',
                'industry': 'PPE Supplier',
                'notes': 'Industrial division is a major distributor of gloves and PPE. Key Products: Industrial & Medical-Grade Gloves. Contact Info: (Look for "Industrial Products" dept.)',
                'website': 'https://bridgestone.co.za',
            },
            {
                'name': 'Netcare Supply Chain',
                'industry': 'Hospital Group',
                'notes': 'Procures for own hospitals; contact for potential external supply. Key Products: Various medical gloves in bulk. Contact Info: (Search for procurement/supply chain dept.)',
                'website': 'https://netcare.co.za',
            },
            {
                'name': 'Life Healthcare Procurement',
                'industry': 'Hospital Group',
                'notes': 'Large private hospital group with a major procurement division. Key Products: Various medical gloves in bulk. Contact Info: (Search for procurement/supply chain dept.)',
                'website': 'https://lifehealthcare.co.za',
            },
            {
                'name': 'Lasec SA',
                'industry': 'Medical Supplier',
                'notes': 'Supplier of laboratory and medical equipment. Key Products: Specimen containers and lab supplies.',
                'website': 'https://lasec.co.za',
            },
        ]

        for data in suppliers_data:
            supplier, created = Supplier.objects.get_or_create(
                name=data['name'],
                defaults={
                    'industry': data['industry'],
                    'notes': data['notes'],
                    'website': data['website'],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created supplier: {supplier.name}'))
            else:
                # Update existing supplier
                supplier.industry = data['industry']
                supplier.notes = data['notes']
                supplier.website = data['website']
                supplier.save()
                self.stdout.write(self.style.WARNING(f'Updated supplier: {supplier.name}'))

        self.stdout.write(self.style.SUCCESS('Supplier population completed.'))
