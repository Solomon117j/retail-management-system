import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from procurement.models import Supplier


class Command(BaseCommand):
    help = 'Generate 50 South African medical suppliers with enterprise-ready information'

    def handle(self, *args, **options):
        # All 50 South African medical suppliers data
        supplier_data = [
            # Major Pharmaceutical Suppliers & Distributors (1-10)
            {
                'name': 'Aspen Pharmacare',
                'contact_person': 'Stephen Saad',
                'email': 'procurement@aspenpharma.com',
                'phone': '+27-11-239-9000',
                'address': 'Aspen Place, 9 Rydall Vale Avenue, Douglasdale, Gauteng 2191',
                'payment_terms': 'Net 30',
                'industry': 'Pharmaceutical Manufacturing',
                'website': 'https://www.aspenpharma.com',
                'tax_id': 'SA123456789',
                'notes': 'Largest African pharmaceutical manufacturer with global presence.'
            },
            {
                'name': 'Adcock Ingram',
                'contact_person': 'Andy Hall',
                'email': 'supply@adcock.com',
                'phone': '+27-11-635-0000',
                'address': '1 New Road, Crown Mines, Johannesburg, 2091',
                'payment_terms': 'Net 30',
                'industry': 'Pharmaceuticals',
                'website': 'https://www.adcock.com',
                'tax_id': 'SA987654321',
                'notes': 'Leading South African pharmaceutical manufacturer and distributor.'
            },
            {
                'name': 'Dis-Chem Pharmacies',
                'contact_person': 'Ivan Saltzman',
                'email': 'wholesale@dischem.co.za',
                'phone': '+27-11-709-0000',
                'address': 'Dis-Chem House, 23 Strijdom Park, Randburg, 2194',
                'payment_terms': 'Net 45',
                'industry': 'Pharmaceutical Distribution',
                'website': 'https://www.dischem.co.za',
                'tax_id': 'SA456789123',
                'notes': 'Major retail pharmacy chain with extensive wholesale division.'
            },
            {
                'name': 'Clicks Group',
                'contact_person': 'Bertina Engelbrecht',
                'email': 'procurement@clicks.co.za',
                'phone': '+27-21-460-1911',
                'address': 'Cnr Searle and Pontac Streets, Cape Town, 7925',
                'payment_terms': 'Net 30',
                'industry': 'Pharmaceutical Retail',
                'website': 'https://www.clicksgroup.co.za',
                'tax_id': 'SA789123456',
                'notes': 'Leading pharmacy retail group with wholesale operations.'
            },
            {
                'name': 'Sigma Pharmaceuticals',
                'contact_person': 'Shane Lofthouse',
                'email': 'orders@sigmapharma.co.za',
                'phone': '+27-11-407-3000',
                'address': '1 Platinum Street, Alrode, Alberton, 1451',
                'payment_terms': 'Net 30',
                'industry': 'Pharmaceutical Wholesale',
                'website': 'https://www.sigmapharmaceuticals.co.za',
                'tax_id': 'SA321654987',
                'notes': 'Comprehensive pharmaceutical wholesaler and distributor.'
            },
            {
                'name': 'Imperial Health Sciences',
                'contact_person': 'Mohammed Akoojee',
                'email': 'healthsciences@imperial.co.za',
                'phone': '+27-11-442-7000',
                'address': 'Imperial Place, 79 Boeing Road East, Bedfordview, 2007',
                'payment_terms': 'Net 45',
                'industry': 'Healthcare Logistics',
                'website': 'https://www.imperialhealthsciences.co.za',
                'tax_id': 'SA654321789',
                'notes': 'Healthcare logistics and pharmaceutical distribution specialist.'
            },
            {
                'name': 'Bidvest Steiner',
                'contact_person': 'Grant Tremeer',
                'email': 'medical@bidveststeiner.co.za',
                'phone': '+27-11-203-6000',
                'address': '1 Steiner Street, Alrode, Alberton, 1451',
                'payment_terms': 'Net 30',
                'industry': 'Medical Supplies',
                'website': 'https://www.bidveststeiner.co.za',
                'tax_id': 'SA987456321',
                'notes': 'Comprehensive medical supplies and equipment distributor.'
            },
            {
                'name': 'Mediclinic Southern Africa',
                'contact_person': 'Dr. Gerrit de Villiers',
                'email': 'procurement@mediclinic.co.za',
                'phone': '+27-21-809-6500',
                'address': '35 Wale Street, Cape Town, 8001',
                'payment_terms': 'Net 60',
                'industry': 'Healthcare Services',
                'website': 'https://www.mediclinic.co.za',
                'tax_id': 'SA147258369',
                'notes': 'Private hospital group with extensive medical supply chain.'
            },
            {
                'name': 'Netcare',
                'contact_person': 'Dr. Richard Friedland',
                'email': 'supplychain@netcare.co.za',
                'phone': '+27-11-301-0000',
                'address': '76 Maude Street, Sandton, 2196',
                'payment_terms': 'Net 60',
                'industry': 'Healthcare Services',
                'website': 'https://www.netcare.co.za',
                'tax_id': 'SA369258147',
                'notes': 'Leading private healthcare provider and medical supplier.'
            },
            {
                'name': 'Life Healthcare',
                'contact_person': 'Adam Pyle',
                'email': 'procurement@lifehealthcare.co.za',
                'phone': '+27-11-219-9000',
                'address': '1 Morningside Place, Morningside, Sandton, 2057',
                'payment_terms': 'Net 60',
                'industry': 'Healthcare Services',
                'website': 'https://www.lifehealthcare.co.za',
                'tax_id': 'SA963852741',
                'notes': 'Private hospital group with comprehensive medical supplies.'
            },

            # Medical Equipment & Device Suppliers (11-20)
            {
                'name': 'Lacto Healthcare',
                'contact_person': 'David Lasker',
                'email': 'sales@lactohealthcare.co.za',
                'phone': '+27-11-444-2200',
                'address': '1 Kikuyu Road, Sunninghill, Sandton, 2157',
                'payment_terms': 'Net 45',
                'industry': 'Medical Equipment',
                'website': 'https://www.lactohealthcare.co.za',
                'tax_id': 'SA741963852',
                'notes': 'Leading medical equipment and consumables supplier.'
            },
            {
                'name': 'Medi-Clinic Equipment',
                'contact_person': 'Dr. Sarah van der Merwe',
                'email': 'equipment@mediclinic.co.za',
                'phone': '+27-11-883-1200',
                'address': '25 Healthcare Road, Midrand, 1685',
                'payment_terms': 'Net 45',
                'industry': 'Medical Equipment',
                'website': 'https://www.mediclinic.co.za',
                'tax_id': 'SA159753468',
                'notes': 'Specialized medical equipment for healthcare facilities.'
            },
            {
                'name': 'SMS Medical Supplies',
                'contact_person': 'Michael Botha',
                'email': 'info@smsmedical.co.za',
                'phone': '+27-11-794-5450',
                'address': '25 Skeen Boulevard, Bedfordview, Johannesburg, 2007',
                'payment_terms': 'Net 30',
                'industry': 'Surgical Equipment',
                'website': 'https://www.smsmedical.co.za',
                'tax_id': 'SA753159846',
                'notes': 'Surgical and medical equipment specialists.'
            },
            {
                'name': 'Medi-K',
                'contact_person': 'Karen de Wet',
                'email': 'procurement@medi-k.co.za',
                'phone': '+27-11-886-2700',
                'address': '2 Electron Avenue, Isando, Kempton Park, 1600',
                'payment_terms': 'Net 30',
                'industry': 'Healthcare Products',
                'website': 'https://www.medi-k.co.za',
                'tax_id': 'SA468135792',
                'notes': 'Comprehensive healthcare products and equipment supplier.'
            },
            {
                'name': 'Medshop',
                'contact_person': 'James Patterson',
                'email': 'orders@medshop.co.za',
                'phone': '+27-87-350-4000',
                'address': '1 Medshop Way, Century City, Cape Town, 7441',
                'payment_terms': 'Net 30',
                'industry': 'Medical Supplies',
                'website': 'https://www.medshop.co.za',
                'tax_id': 'SA792468135',
                'notes': 'Medical equipment and supplies online retailer.'
            },
            {
                'name': 'Surgical Holdings',
                'contact_person': 'Dr. Peter van Niekerk',
                'email': 'orders@surgicalholdings.co.za',
                'phone': '+27-11-444-5555',
                'address': '15 Roper Street, Cleveland, Johannesburg, 2022',
                'payment_terms': 'Net 45',
                'industry': 'Surgical Instruments',
                'website': 'https://www.surgicalholdings.co.za',
                'tax_id': 'SA135792468',
                'notes': 'Premium surgical instruments and operating room equipment.'
            },
            {
                'name': 'Tissue Science Laboratories',
                'contact_person': 'Dr. Amanda Naidoo',
                'email': 'sales@tsl.co.za',
                'phone': '+27-11-234-5678',
                'address': '12 Science Park Road, Persequor, Pretoria, 0020',
                'payment_terms': 'Net 30',
                'industry': 'Medical Devices',
                'website': 'https://www.tsl.co.za',
                'tax_id': 'SA246813579',
                'notes': 'Medical devices and specialized laboratory equipment.'
            },
            {
                'name': 'Medi-Save',
                'contact_person': 'Robert Williams',
                'email': 'supplies@medisave.co.za',
                'phone': '+27-11-555-1234',
                'address': '8 Health Street, Wynberg, Sandton, 2090',
                'payment_terms': 'Net 30',
                'industry': 'Medical Supplies',
                'website': 'https://www.medisave.co.za',
                'tax_id': 'SA579246813',
                'notes': 'Cost-effective medical supplies and equipment.'
            },
            {
                'name': 'Surgical Systems',
                'contact_person': 'Dr. Mark Thompson',
                'email': 'info@surgicalsystems.co.za',
                'phone': '+27-11-333-4444',
                'address': '45 Operation Avenue, Midrand, 1685',
                'payment_terms': 'Net 45',
                'industry': 'Surgical Equipment',
                'website': 'https://www.surgicalsystems.co.za',
                'tax_id': 'SA813579246',
                'notes': 'Operating theater equipment and surgical systems.'
            },
            {
                'name': 'Dental City',
                'contact_person': 'Dr. Lisa Cohen',
                'email': 'orders@dentalcity.co.za',
                'phone': '+27-11-888-9999',
                'address': '32 Tooth Street, Randburg, 2194',
                'payment_terms': 'Net 30',
                'industry': 'Dental Equipment',
                'website': 'https://www.dentalcity.co.za',
                'tax_id': 'SA357924681',
                'notes': 'Dental equipment and supplies specialist.'
            },

            # Laboratory & Diagnostic Suppliers (21-30)
            {
                'name': 'Lancet Laboratories',
                'contact_person': 'Dr. Tshepo Motsohi',
                'email': 'supplies@lancet.co.za',
                'phone': '+27-11-358-0000',
                'address': '22 Wellington Road, Parktown, Johannesburg, 2193',
                'payment_terms': 'Net 30',
                'industry': 'Laboratory Services',
                'website': 'https://www.lancet.co.za',
                'tax_id': 'SA924681357',
                'notes': 'Leading pathology laboratory services and supplies.'
            },
            {
                'name': 'Ampath Laboratories',
                'contact_person': 'Dr. Hendrik Hanekom',
                'email': 'procurement@ampath.co.za',
                'phone': '+27-12-420-0000',
                'address': 'Ampath House, 225 Veale Street, Pretoria, 0027',
                'payment_terms': 'Net 30',
                'industry': 'Pathology Services',
                'website': 'https://www.ampath.co.za',
                'tax_id': 'SA681357924',
                'notes': 'Comprehensive pathology and laboratory services.'
            },
            {
                'name': 'Pathcare',
                'contact_person': 'Dr. Susan van Zyl',
                'email': 'supply@pathcare.co.za',
                'phone': '+27-21-658-5000',
                'address': 'Pathcare House, 1 Pathcare Lane, Tygerberg, Cape Town, 7505',
                'payment_terms': 'Net 30',
                'industry': 'Pathology Services',
                'website': 'https://www.pathcare.co.za',
                'tax_id': 'SA468235791',
                'notes': 'National pathology laboratory network.'
            },
            {
                'name': 'Labotec',
                'contact_person': 'Susan Pretorius',
                'email': 'sales@labotec.co.za',
                'phone': '+27-11-444-2828',
                'address': '1 Montgomery Drive, Montague Gardens, Cape Town, 7441',
                'payment_terms': 'Net 45',
                'industry': 'Laboratory Equipment',
                'website': 'https://www.labotec.co.za',
                'tax_id': 'SA791357924',
                'notes': 'Laboratory equipment and scientific supplies.'
            },
            {
                'name': 'Lasec',
                'contact_person': 'Johnathan Barnes',
                'email': 'orders@lasec.com',
                'phone': '+27-21-763-3900',
                'address': '1 Electron Road, Technopark, Stellenbosch, 7600',
                'payment_terms': 'Net 30',
                'industry': 'Laboratory Equipment',
                'website': 'https://www.lasec.com',
                'tax_id': 'SA924681358',
                'notes': 'Laboratory equipment and consumables supplier.'
            },
            {
                'name': 'Lennox Laboratory Supplies',
                'contact_person': 'Brian Lennox',
                'email': 'info@lennox.co.za',
                'phone': '+27-11-615-8000',
                'address': '7 Rietspruit Road, Alrode, Alberton, 1451',
                'payment_terms': 'Net 30',
                'industry': 'Laboratory Supplies',
                'website': 'https://www.lennox.co.za',
                'tax_id': 'SA357924682',
                'notes': 'Laboratory supplies and equipment distributor.'
            },
            {
                'name': 'Radlab',
                'contact_person': 'Dr. Michael Botha',
                'email': 'equipment@radlab.co.za',
                'phone': '+27-11-484-2000',
                'address': 'Radlab House, 1 Imaging Street, Parktown, Johannesburg, 2193',
                'payment_terms': 'Net 60',
                'industry': 'Diagnostic Equipment',
                'website': 'https://www.radlab.co.za',
                'tax_id': 'SA682468135',
                'notes': 'Radiology and diagnostic imaging equipment.'
            },
            {
                'name': 'Siemens Healthineers SA',
                'contact_person': 'Megan Cruywagen',
                'email': 'za.healthcare@siemens.com',
                'phone': '+27-11-652-2000',
                'address': 'Siemens House, 106 Charles Crescent, Eastgate, Sandton, 2148',
                'payment_terms': 'Net 60',
                'industry': 'Medical Imaging',
                'website': 'https://www.siemens-healthineers.com',
                'tax_id': 'SA135792470',
                'notes': 'Advanced medical imaging equipment and healthcare technology.'
            },
            {
                'name': 'GE Healthcare South Africa',
                'contact_person': 'Thabiso Mokoena',
                'email': 'za.orders@gehealthcare.com',
                'phone': '+27-11-237-7000',
                'address': 'GE Healthcare House, 1 Arnold Road, Sandton, 2196',
                'payment_terms': 'Net 60',
                'industry': 'Medical Technology',
                'website': 'https://www.gehealthcare.co.za',
                'tax_id': 'SA468135794',
                'notes': 'Global medical technology and digital solutions.'
            },
            {
                'name': 'Philips Healthcare SA',
                'contact_person': 'Nomsa Dlamini',
                'email': 'healthcare.za@philips.com',
                'phone': '+27-11-471-5000',
                'address': 'Philips House, 216 14th Road, Noordwyk, Midrand, 1685',
                'payment_terms': 'Net 60',
                'industry': 'Medical Equipment',
                'website': 'https://www.philips.co.za',
                'tax_id': 'SA792468137',
                'notes': 'Healthcare technology and medical systems.'
            },

            # Specialized Medical Suppliers (31-40)
            {
                'name': 'Baxter Healthcare SA',
                'contact_person': 'David Cohen',
                'email': 'za.customerservice@baxter.com',
                'phone': '+27-11-397-4000',
                'address': 'Baxter House, 1 The Straight, Steeldale, Johannesburg, 2197',
                'payment_terms': 'Net 45',
                'industry': 'Hospital Products',
                'website': 'https://www.baxter.com',
                'tax_id': 'SA246813580',
                'notes': 'Hospital products, medications, and clinical nutrition.'
            },
            {
                'name': 'Fresenius Kabi SA',
                'contact_person': 'Annette Schmidt',
                'email': 'za.info@fresenius-kabi.com',
                'phone': '+27-11-397-3000',
                'address': '1 Platinum Street, Alrode, Alberton, 1451',
                'payment_terms': 'Net 45',
                'industry': 'Pharmaceuticals',
                'website': 'https://www.fresenius-kabi.com/za',
                'tax_id': 'SA579246814',
                'notes': 'Infusion therapy and clinical nutrition specialists.'
            },
            {
                'name': 'Johnson & Johnson South Africa',
                'contact_person': 'Lerato Moloi',
                'email': 'za.medtech@its.jnj.com',
                'phone': '+27-11-661-4111',
                'address': '1 Ncondo Place, Umhlanga Ridge, Durban, 4319',
                'payment_terms': 'Net 60',
                'industry': 'Medical Devices',
                'website': 'https://www.jnj.com',
                'tax_id': 'SA813579247',
                'notes': 'Medical devices, pharmaceuticals, and consumer health products.'
            },
            {
                'name': 'Abbott Laboratories SA',
                'contact_person': 'Katherine van Rensburg',
                'email': 'za.orders@abbott.com',
                'phone': '+27-11-921-6000',
                'address': 'Abbott Place, 1 Healthcare Road, Midrand, 1685',
                'payment_terms': 'Net 45',
                'industry': 'Healthcare Products',
                'website': 'https://www.abbott.com',
                'tax_id': 'SA357924683',
                'notes': 'Healthcare products, nutrition, and diagnostics.'
            },
            {
                'name': 'Roche Products SA',
                'contact_person': 'Dr. Werner Bock',
                'email': 'za.info@roche.com',
                'phone': '+27-11-928-7700',
                'address': 'Roche House, 1 Roche Drive, Sandton, 2196',
                'payment_terms': 'Net 60',
                'industry': 'Pharmaceuticals',
                'website': 'https://www.roche.com',
                'tax_id': 'SA924681359',
                'notes': 'Pharmaceuticals and diagnostic solutions.'
            },
            {
                'name': 'Novartis South Africa',
                'contact_person': 'Dr. Prasanna Kari',
                'email': 'za.supply@novartis.com',
                'phone': '+27-11-929-5000',
                'address': 'Novartis House, 15 Hulbert Road, New Centre, Johannesburg, 2001',
                'payment_terms': 'Net 60',
                'industry': 'Pharmaceuticals',
                'website': 'https://www.novartis.com',
                'tax_id': 'SA681357925',
                'notes': 'Innovative medicines and healthcare solutions.'
            },
            {
                'name': 'Pfizer South Africa',
                'contact_person': 'Rhulani Nhlapo',
                'email': 'za.orders@pfizer.com',
                'phone': '+27-11-320-6000',
                'address': 'Pfizer House, 1 Pfizer Lane, Sandton, 2196',
                'payment_terms': 'Net 60',
                'industry': 'Pharmaceuticals',
                'website': 'https://www.pfizer.com',
                'tax_id': 'SA468235792',
                'notes': 'Biopharmaceutical innovations and medications.'
            },
            {
                'name': 'Sanofi South Africa',
                'contact_person': 'Dr. Niresh Bechan',
                'email': 'za.procurement@sanofi.com',
                'phone': '+27-11-256-3600',
                'address': 'Sanofi House, 22 Georgian Crescent, Bryanston, Sandton, 2191',
                'payment_terms': 'Net 60',
                'industry': 'Healthcare',
                'website': 'https://www.sanofi.com',
                'tax_id': 'SA791357925',
                'notes': 'Healthcare and pharmaceutical innovations.'
            },
            {
                'name': 'GlaxoSmithKline South Africa',
                'contact_person': 'Dr. Tumi Msimang',
                'email': 'za.supply@gsk.com',
                'phone': '+27-11-745-6000',
                'address': 'GSK House, 1 GSK Avenue, Midrand, 1685',
                'payment_terms': 'Net 60',
                'industry': 'Pharmaceuticals',
                'website': 'https://www.gsk.com',
                'tax_id': 'SA924681360',
                'notes': 'Pharmaceuticals, vaccines, and consumer healthcare.'
            },
            {
                'name': 'Merck South Africa',
                'contact_person': 'Dr. Sipho Dlamini',
                'email': 'za.orders@merckgroup.com',
                'phone': '+27-11-655-3000',
                'address': 'Merck House, 12 Science Road, Persequor, Pretoria, 0020',
                'payment_terms': 'Net 60',
                'industry': 'Healthcare',
                'website': 'https://www.merckgroup.com',
                'tax_id': 'SA357924684',
                'notes': 'Healthcare, life sciences, and performance materials.'
            },

            # Additional Medical Suppliers (41-50)
            {
                'name': 'Beiersdorf South Africa',
                'contact_person': 'Sarah Johnson',
                'email': 'za.medical@beiersdorf.com',
                'phone': '+27-11-921-1400',
                'address': 'Beiersdorf House, 25 Medical Road, Isando, 1600',
                'payment_terms': 'Net 45',
                'industry': 'Wound Care',
                'website': 'https://www.beiersdorf.com',
                'tax_id': 'SA681357926',
                'notes': 'Wound care products and medical supplies.'
            },
            {
                'name': 'Smith & Nephew South Africa',
                'contact_person': 'Dr. Mark Williams',
                'email': 'za.orders@smith-nephew.com',
                'phone': '+27-11-444-3300',
                'address': 'Smith & Nephew House, 1 Orthopaedic Street, Midrand, 1685',
                'payment_terms': 'Net 60',
                'industry': 'Medical Devices',
                'website': 'https://www.smith-nephew.com',
                'tax_id': 'SA468235793',
                'notes': 'Advanced medical devices and equipment.'
            },
            {
                'name': 'Stryker South Africa',
                'contact_person': 'Dr. James Peterson',
                'email': 'za.supply@stryker.com',
                'phone': '+27-11-234-5679',
                'address': 'Stryker House, 15 Medical Technology Drive, Sandton, 2196',
                'payment_terms': 'Net 60',
                'industry': 'Medical Technology',
                'website': 'https://www.stryker.com',
                'tax_id': 'SA791357926',
                'notes': 'Medical technology and equipment solutions.'
            },
            {
                'name': 'BD South Africa',
                'contact_person': 'Michelle van der Westhuizen',
                'email': 'za.orders@bd.com',
                'phone': '+27-11-921-7000',
                'address': 'BD House, 1 BD Way, Midrand, 1685',
                'payment_terms': 'Net 45',
                'industry': 'Medical Devices',
                'website': 'https://www.bd.com',
                'tax_id': 'SA924681361',
                'notes': 'Medical devices, instruments, and reagents.'
            },
            {
                'name': 'Medtronic South Africa',
                'contact_person': 'Dr. Arno van der Merwe',
                'email': 'za.supply@medtronic.com',
                'phone': '+27-11-655-4000',
                'address': 'Medtronic House, 1 Medtronic Road, Centurion, 0157',
                'payment_terms': 'Net 60',
                'industry': 'Medical Devices',
                'website': 'https://www.medtronic.com',
                'tax_id': 'SA357924685',
                'notes': 'Medical device company specializing in chronic disease treatment.'
            },
            {
                'name': 'Med-e-Mass',
                'contact_person': 'Riaan van der Merwe',
                'email': 'sales@med-e-mass.co.za',
                'phone': '+27-12-343-7100',
                'address': '1 Karee Street, Technopark, Stellenbosch, 7600',
                'payment_terms': 'Net 30',
                'industry': 'Medical Equipment',
                'website': 'https://www.med-e-mass.co.za',
                'tax_id': 'SA681357927',
                'notes': 'Medical equipment and healthcare supplies distributor.'
            },
            {
                'name': 'SASOL Medcare',
                'contact_person': 'Fleetwood Grobler',
                'email': 'medcare@sasol.com',
                'phone': '+27-11-441-3111',
                'address': 'Sasol Place, 1 Sturdee Avenue, Rosebank, Johannesburg, 2196',
                'payment_terms': 'Net 45',
                'industry': 'Healthcare Products',
                'website': 'https://www.sasol.com',
                'tax_id': 'SA468235794',
                'notes': 'Healthcare products and occupational health services.'
            },
            {
                'name': 'Alpha Pharm',
                'contact_person': 'Gary Friedman',
                'email': 'orders@alphapharm.co.za',
                'phone': '+27-11-922-3000',
                'address': 'Alpha House, 6 Hulbert Road, New Centre, Johannesburg, 2001',
                'payment_terms': 'Net 30',
                'industry': 'Pharmaceutical Manufacturing',
                'website': 'https://www.alphapharm.co.za',
                'tax_id': 'SA791357927',
                'notes': 'Pharmaceutical manufacturing and distribution company.'
            },
            {
                'name': 'Cipla Medpro',
                'contact_person': 'Paul Miller',
                'email': 'supply@ciplamedpro.co.za',
                'phone': '+27-31-580-5400',
                'address': 'Cipla House, 1 Magwa Crescent, Waterfall City, Midrand, 1685',
                'payment_terms': 'Net 30',
                'industry': 'Pharmaceuticals',
                'website': 'https://www.cipla.co.za',
                'tax_id': 'SA924681362',
                'notes': 'Pharmaceutical company with focus on affordable medications.'
            },
            {
                'name': 'Virbac South Africa',
                'contact_person': 'Dr. Pierre van Zyl',
                'email': 'za.orders@virbac.com',
                'phone': '+27-11-807-4400',
                'address': 'Virbac House, 1 Veterinary Road, Centurion, 0157',
                'payment_terms': 'Net 30',
                'industry': 'Veterinary Products',
                'website': 'https://www.virbac.com',
                'tax_id': 'SA357924686',
                'notes': 'Animal health and veterinary pharmaceutical products.'
            }
        ]

        suppliers_created = 0
        for supp_data in supplier_data:
            # Generate contract start date (random within last 2 years)
            contract_start_date = date.today() - timedelta(days=random.randint(0, 730))

            # Create supplier with enterprise-ready fields
            supplier, created = Supplier.objects.get_or_create(
                name=supp_data['name'],
                defaults={
                    'contact_person': supp_data['contact_person'],
                    'email': supp_data['email'],
                    'phone': supp_data['phone'],
                    'address': supp_data['address'],
                    'contract_start_date': contract_start_date,
                    'payment_terms': supp_data['payment_terms'],
                    'industry': supp_data['industry'],
                    'website': supp_data['website'],
                    'tax_id': supp_data['tax_id'],
                    'notes': supp_data['notes'],
                    'is_active': True,
                    'on_time_delivery_rate': round(random.uniform(85.0, 98.0), 2),
                    'quality_rating': random.choice([3.5, 4.0, 4.5, 5.0]),
                    'compliance_score': round(random.uniform(90.0, 100.0), 2),
                    'total_orders': random.randint(50, 500),
                    'total_spent': round(random.uniform(50000.00, 500000.00), 2),
                }
            )
            if created:
                suppliers_created += 1
                self.stdout.write(self.style.SUCCESS(
                    f'Created supplier: {supplier.name} ({supplier.industry}) - Rating: {supplier.quality_rating}/5'
                ))
            else:
                self.stdout.write(self.style.WARNING(f'Supplier already exists: {supplier.name}'))

        self.stdout.write(self.style.SUCCESS(
            f'Successfully processed {len(supplier_data)} South African medical suppliers. Created {suppliers_created} new suppliers.'
        ))