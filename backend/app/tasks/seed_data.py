import os
import json
from datetime import datetime
from app.db.session import SessionLocal
from app.models.manufacturer import Manufacturer
from app.models.medicine import Medicine
from sqlalchemy import text

# Define 60 companies (30 US, 30 Indian)
companies = [
    # 20 US Approved
    {'name': 'PFIZER INC.', 'email': 'brandprotection@pfizer.com', 'auth': 'Albert Bourla (CEO)', 'wallet': '0x11C7656EC7ab88b098defB751B7401B5f6d8976F', 'status': 'APPROVED', 'verified': True},
    {'name': 'AMGEN INC.', 'email': 'security@amgen.com', 'auth': 'Robert A. Bradway (CEO)', 'wallet': '0x22C7656EC7ab88b098defB751B7401B5f6d8976F', 'status': 'APPROVED', 'verified': True},
    {'name': 'GILEAD SCIENCES INC.', 'email': 'security@gilead.com', 'auth': 'Daniel O Day (CEO)', 'wallet': '0x33C7656EC7ab88b098defB751B7401B5f6d8976F', 'status': 'APPROVED', 'verified': True},
    {'name': 'MODERNA INC.', 'email': 'security@modernatx.com', 'auth': 'Stephane Bancel (CEO)', 'wallet': '0x44C7656EC7ab88b098defB751B7401B5f6d8976F', 'status': 'APPROVED', 'verified': True},
    {'name': 'BIOGEN INC.', 'email': 'security@biogen.com', 'auth': 'Christopher A. Viehbacher (CEO)', 'wallet': '0x55C7656EC7ab88b098defB751B7401B5f6d8976F', 'status': 'APPROVED', 'verified': True},
    {'name': 'REGENERON PHARMACEUTICALS', 'email': 'security@regeneron.com', 'auth': 'Leonard S. Schleifer (CEO)', 'wallet': '0x66C7656EC7ab88b098defB751B7401B5f6d8976F', 'status': 'APPROVED', 'verified': True},
    {'name': 'VERTEX PHARMACEUTICALS', 'email': 'security@vrtx.com', 'auth': 'Reshma Kewalramani (CEO)', 'wallet': '0x77C7656EC7ab88b098defB751B7401B5f6d8976F', 'status': 'APPROVED', 'verified': True},
    {'name': 'VIATRIS INC.', 'email': 'security@viatris.com', 'auth': 'Scott A. Smith (CEO)', 'wallet': '0x88C7656EC7ab88b098defB751B7401B5f6d8976F', 'status': 'APPROVED', 'verified': True},
    {'name': 'ALEXION PHARMACEUTICALS', 'email': 'security@alexion.com', 'auth': 'Marc Dunoyer (CEO)', 'wallet': '0x99C7656EC7ab88b098defB751B7401B5f6d8976F', 'status': 'APPROVED', 'verified': True},
    {'name': 'INCYTE CORPORATION', 'email': 'security@incyte.com', 'auth': 'Herve Hoppenot (CEO)', 'wallet': '0x10C7656EC7ab88b098defB751B7401B5f6d8976F', 'status': 'APPROVED', 'verified': True},
    {'name': 'BIOMARIN PHARMACEUTICAL', 'email': 'security@bmrn.com', 'auth': 'Jean-Jacques Bienaime (CEO)', 'wallet': '0x12C7656EC7ab88b098defB751B7401B5f6d8976F', 'status': 'APPROVED', 'verified': True},
    {'name': 'SEAGEN INC.', 'email': 'security@seagen.com', 'auth': 'David Epstein (CEO)', 'wallet': '0x13C7656EC7ab88b098defB751B7401B5f6d8976F', 'status': 'APPROVED', 'verified': True},
    {'name': 'ORGANON & CO.', 'email': 'security@organon.com', 'auth': 'Kevin Ali (CEO)', 'wallet': '0x14C7656EC7ab88b098defB751B7401B5f6d8976F', 'status': 'APPROVED', 'verified': True},
    {'name': 'JAZZ PHARMACEUTICALS', 'email': 'security@jazzpharma.com', 'auth': 'Bruce Cozadd (CEO)', 'wallet': '0x15C7656EC7ab88b098defB751B7401B5f6d8976F', 'status': 'APPROVED', 'verified': True},
    {'name': 'HORIZON THERAPEUTICS', 'email': 'security@horizontherapeutics.com', 'auth': 'Timothy P. Walbert (CEO)', 'wallet': '0x16C7656EC7ab88b098defB751B7401B5f6d8976F', 'status': 'APPROVED', 'verified': True},
    # 5 Pending US
    {'name': 'JOHNSON & JOHNSON', 'email': 'security@jnj.com', 'auth': 'Dr. Paul Stoffels (Chief Scientific Officer)', 'wallet': '0x71C7656EC7ab88b098defB751B7401B5f6d8976F', 'status': 'UNVERIFIED', 'verified': False},
    {'name': 'MERCK & CO. INC.', 'email': 'security@merck.com', 'auth': 'Robert M. Davis (CEO)', 'wallet': '0x32A39828d54166753075f137bd7342c73f7A901c', 'status': 'UNVERIFIED', 'verified': False},
    {'name': 'ABBVIE INC.', 'email': 'security@abbvie.com', 'auth': 'Richard A. Gonzalez (CEO)', 'wallet': '0x2546BcD3c84621e909000a55D39947936f4E3b3d', 'status': 'UNVERIFIED', 'verified': False},
    {'name': 'BRISTOL MYERS SQUIBB', 'email': 'security@bms.com', 'auth': 'Giovanni Caforio (CEO)', 'wallet': '0x45C7656EC7ab88b098defB751B7401B5f6d8976G', 'status': 'UNVERIFIED', 'verified': False},
    {'name': 'ELI LILLY AND COMPANY', 'email': 'security@lilly.com', 'auth': 'David A. Ricks (CEO)', 'wallet': '0x35B39828d54166753075f137bd7342c73f7A901p', 'status': 'UNVERIFIED', 'verified': False},
    # 10 New US Companies
    {'name': 'BAXTER INTERNATIONAL INC.', 'email': 'security@baxter.com', 'auth': 'Jose E. Almeida (CEO)', 'wallet': '0x17C7656EC7ab88b098defB751B7401B5f6d8976F', 'status': 'APPROVED', 'verified': True},
    {'name': 'ALKERMES PLC', 'email': 'security@alkermes.com', 'auth': 'Richard Pops (CEO)', 'wallet': '0x18C7656EC7ab88b098defB751B7401B5f6d8976F', 'status': 'APPROVED', 'verified': True},
    {'name': 'MYLAN PHARMACEUTICALS', 'email': 'security@mylan.com', 'auth': 'Heather Bresch (CEO)', 'wallet': '0x19C7656EC7ab88b098defB751B7401B5f6d8976F', 'status': 'APPROVED', 'verified': True},
    {'name': 'SANOFI US SERVICES', 'email': 'security@sanofi.com', 'auth': 'Paul Hudson (CEO)', 'wallet': '0x20C7656EC7ab88b098defB751B7401B5f6d8976F', 'status': 'APPROVED', 'verified': True},
    {'name': 'GLAXOSMITHKLINE US', 'email': 'security@gsk.com', 'auth': 'Emma Walmsley (CEO)', 'wallet': '0x21C7656EC7ab88b098defB751B7401B5f6d8976F', 'status': 'APPROVED', 'verified': True},
    {'name': 'NOVARTIS PHARMA US', 'email': 'security@novartis.com', 'auth': 'Vasant Narasimhan (CEO)', 'wallet': '0x22C7656EC7ab88b098defB751B7401B5f6d8976F', 'status': 'APPROVED', 'verified': True},
    {'name': 'MERCK SHARP & DOHME', 'email': 'security@msd.com', 'auth': 'Rob Davis (CEO)', 'wallet': '0x23C7656EC7ab88b098defB751B7401B5f6d8976F', 'status': 'APPROVED', 'verified': True},
    {'name': 'ASTRAZENECA US', 'email': 'security@astrazeneca.com', 'auth': 'Pascal Soriot (CEO)', 'wallet': '0x24C7656EC7ab88b098defB751B7401B5f6d8976F', 'status': 'APPROVED', 'verified': True},
    {'name': 'TAKEDA PHARMACEUTICALS US', 'email': 'security@takeda.com', 'auth': 'Christophe Weber (CEO)', 'wallet': '0x25C7656EC7ab88b098defB751B7401B5f6d8976F', 'status': 'APPROVED', 'verified': True},
    {'name': 'BOEHRINGER INGELHEIM US', 'email': 'security@boehringer.com', 'auth': 'Hubertus von Baumbach (CEO)', 'wallet': '0x26C7656EC7ab88b098defB751B7401B5f6d8976F', 'status': 'APPROVED', 'verified': True},

    # 20 Approved Indian
    {'name': 'SUN PHARMACEUTICAL INDUSTRIES LTD.', 'email': 'security@sunpharma.com', 'auth': 'Dilip Shanghvi (MD)', 'wallet': '0x22C7656EC7ab88b098defB751B7401B5f6d8976G', 'status': 'APPROVED', 'verified': True},
    {'name': 'DR. REDDYS LABORATORIES LTD.', 'email': 'security@drreddys.com', 'auth': 'G.V. Prasad (Co-Chairman)', 'wallet': '0x33C7656EC7ab88b098defB751B7401B5f6d8976G', 'status': 'APPROVED', 'verified': True},
    {'name': 'LUPIN LIMITED', 'email': 'security@lupin.com', 'auth': 'Nilesh Gupta (MD)', 'wallet': '0x44C7656EC7ab88b098defB751B7401B5f6d8976G', 'status': 'APPROVED', 'verified': True},
    {'name': 'MANKIND PHARMA LTD.', 'email': 'security@mankindpharma.com', 'auth': 'Rajeev Juneja (VC)', 'wallet': '0x55C7656EC7ab88b098defB751B7401B5f6d8976G', 'status': 'APPROVED', 'verified': True},
    {'name': 'PFIZER LIMITED', 'email': 'security@pfizerindia.com', 'auth': 'Meenakshi Nevatia (MD)', 'wallet': '0x66C7656EC7ab88b098defB751B7401B5f6d8976G', 'status': 'APPROVED', 'verified': True},
    {'name': 'MACLEODS PHARMACEUTICALS LTD.', 'email': 'security@macleods.com', 'auth': 'G. Agarwal (Director)', 'wallet': '0x77C7656EC7ab88b098defB751B7401B5f6d8976G', 'status': 'APPROVED', 'verified': True},
    {'name': 'ARISTO PHARMACEUTICALS', 'email': 'security@aristo.com', 'auth': 'U.K. Prasad (Director)', 'wallet': '0x88C7656EC7ab88b098defB751B7401B5f6d8976G', 'status': 'APPROVED', 'verified': True},
    {'name': 'CIPLA LIMITED', 'email': 'security@cipla.com', 'auth': 'Umang Vohra (CEO)', 'wallet': '0x99C7656EC7ab88b098defB751B7401B5f6d8976G', 'status': 'APPROVED', 'verified': True},
    {'name': 'TORRENT PHARMACEUTICALS LTD.', 'email': 'security@torrent.com', 'auth': 'Samir Mehta (Chairman)', 'wallet': '0x10C7656EC7ab88b098defB751B7401B5f6d8976G', 'status': 'APPROVED', 'verified': True},
    {'name': 'GLENMARK PHARMACEUTICALS LTD.', 'email': 'security@glenmark.com', 'auth': 'Glenn Saldanha (MD)', 'wallet': '0x12C7656EC7ab88b098defB751B7401B5f6d8976G', 'status': 'APPROVED', 'verified': True},
    {'name': 'ALKEM LABORATORIES LTD.', 'email': 'security@alkem.com', 'auth': 'Sandeep Singh (MD)', 'wallet': '0x13C7656EC7ab88b098defB751B7401B5f6d8976G', 'status': 'APPROVED', 'verified': True},
    {'name': 'ZYDUS LIFESCIENCES LTD.', 'email': 'security@zydus.com', 'auth': 'Pankaj Patel (Chairman)', 'wallet': '0x14C7656EC7ab88b098defB751B7401B5f6d8976G', 'status': 'APPROVED', 'verified': True},
    {'name': 'BIOCON LIMITED', 'email': 'security@biocon.com', 'auth': 'Kiran Mazumdar-Shaw (MD)', 'wallet': '0x15C7656EC7ab88b098defB751B7401B5f6d8976G', 'status': 'APPROVED', 'verified': True},
    {'name': 'INTAS PHARMACEUTICALS LTD.', 'email': 'security@intas.com', 'auth': 'Binish Chudgar (VC)', 'wallet': '0x16C7656EC7ab88b098defB751B7401B5f6d8976G', 'status': 'APPROVED', 'verified': True},
    {'name': 'AUROBINDO PHARMA LTD.', 'email': 'security@aurobindo.com', 'auth': 'K. Nityananda Reddy (VC)', 'wallet': '0x17C7656EC7ab88b098defB751B7401B5f6d8976G', 'status': 'APPROVED', 'verified': True},
    {'name': 'IPCA LABORATORIES LTD.', 'email': 'security@ipca.com', 'auth': 'Premchand Godha (MD)', 'wallet': '0x18C7656EC7ab88b098defB751B7401B5f6d8976G', 'status': 'APPROVED', 'verified': True},
    {'name': 'ALEMBIC PHARMACEUTICALS LTD.', 'email': 'security@alembic.com', 'auth': 'Pranav Amin (MD)', 'wallet': '0x19C7656EC7ab88b098defB751B7401B5f6d8976G', 'status': 'APPROVED', 'verified': True},
    {'name': 'ABBOTT INDIA LIMITED', 'email': 'security@abbottindia.com', 'auth': 'Anil Joseph (MD)', 'wallet': '0x20C7656EC7ab88b098defB751B7401B5f6d8976G', 'status': 'APPROVED', 'verified': True},
    {'name': 'GLAXOSMITHKLINE PHARMACEUTICALS', 'email': 'security@gskindia.com', 'auth': 'Bhushan Akshikar (MD)', 'wallet': '0x21C7656EC7ab88b098defB751B7401B5f6d8976G', 'status': 'APPROVED', 'verified': True},
    {'name': 'NOVARTIS INDIA LIMITED', 'email': 'security@novartisindia.com', 'auth': 'Sanjay Murdeshwar (MD)', 'wallet': '0x23C7656EC7ab88b098defB751B7401B5f6d8976G', 'status': 'APPROVED', 'verified': True},
    # 10 New Indian Companies
    {'name': 'MICRO LABS LIMITED', 'email': 'security@microlabs.com', 'auth': 'Dilip Surana (CMD)', 'wallet': '0x24C7656EC7ab88b098defB751B7401B5f6d8976G', 'status': 'APPROVED', 'verified': True},
    {'name': 'FDC LIMITED', 'email': 'security@fdc.com', 'auth': 'Mohan A. Chandavarkar (MD)', 'wallet': '0x25C7656EC7ab88b098defB751B7401B5f6d8976G', 'status': 'APPROVED', 'verified': True},
    {'name': 'CORONATION PHARMA', 'email': 'security@coronation.com', 'auth': 'R.K. Gupta (Director)', 'wallet': '0x26C7656EC7ab88b098defB751B7401B5f6d8976G', 'status': 'APPROVED', 'verified': True},
    {'name': 'HETERO DRUGS LTD', 'email': 'security@hetero.com', 'auth': 'B.P.S. Reddy (CMD)', 'wallet': '0x27C7656EC7ab88b098defB751B7401B5f6d8976G', 'status': 'APPROVED', 'verified': True},
    {'name': 'APOTEX RESEARCH INDIA', 'email': 'security@apotex.com', 'auth': 'Jeremy B. Desai (CEO)', 'wallet': '0x28C7656EC7ab88b098defB751B7401B5f6d8976G', 'status': 'APPROVED', 'verified': True},
    {'name': 'SUN PHARMA LABORATORIES', 'email': 'security@sunlabs.com', 'auth': 'Kirti Ganorkar (CEO)', 'wallet': '0x29C7656EC7ab88b098defB751B7401B5f6d8976G', 'status': 'APPROVED', 'verified': True},
    {'name': 'BLUE CROSS LABORATORIES', 'email': 'security@bluecross.com', 'auth': 'N.H. Israni (MD)', 'wallet': '0x30C7656EC7ab88b098defB751B7401B5f6d8976G', 'status': 'APPROVED', 'verified': True},
    {'name': 'EMCURE PHARMACEUTICALS LTD.', 'email': 'security@emcure.com', 'auth': 'Satish Mehta (MD)', 'wallet': '0x31C7656EC7ab88b098defB751B7401B5f6d8976G', 'status': 'APPROVED', 'verified': True},
    {'name': 'AJANTA PHARMA LTD.', 'email': 'security@ajanta.com', 'auth': 'Yogesh Agrawal (MD)', 'wallet': '0x32C7656EC7ab88b098defB751B7401B5f6d8976G', 'status': 'APPROVED', 'verified': True},
    {'name': 'MANKIND SPECIALTIES', 'email': 'security@mankindspec.com', 'auth': 'Sheetal Juneja (Director)', 'wallet': '0x33C7656EC7ab88b098defB751B7401B5f6d8976G', 'status': 'APPROVED', 'verified': True}
]

# Define 2 medicines for each of the 60 companies (Total 120 medicines)
medicines = [
    # 20 US Approved (40 medicines)
    {'batch_id': 'PFIZ-LIP88', 'medicine_name': 'LIPITOR (ATORVASTATIN CALCIUM TABLETS)', 'manufacturer': 'PFIZER INC.', 'exp_date': '2026-12-31', 'region': 'UNITED STATES'},
    {'batch_id': 'PFIZ-LYR99', 'medicine_name': 'LYRICA (PREGABALIN CAPSULES)', 'manufacturer': 'PFIZER INC.', 'exp_date': '2027-04-30', 'region': 'EUROPEAN UNION'},
    {'batch_id': 'AMGN-ENB22', 'medicine_name': 'ENBREL (ETANERCEPT INJECTION)', 'manufacturer': 'AMGEN INC.', 'exp_date': '2026-10-31', 'region': 'NORTH AMERICA'},
    {'batch_id': 'AMGN-NEU33', 'medicine_name': 'NEULASTA (PEGFILGRASTIM INJECTION)', 'manufacturer': 'AMGEN INC.', 'exp_date': '2027-02-28', 'region': 'LATIN AMERICA'},
    {'batch_id': 'GILD-REM11', 'medicine_name': 'VEKLURY (REMDESIVIR INJECTION)', 'manufacturer': 'GILEAD SCIENCES INC.', 'exp_date': '2026-09-30', 'region': 'EAST ASIA'},
    {'batch_id': 'GILD-TRU22', 'medicine_name': 'TRUVADA (EMTRICTABINE TABLETS)', 'manufacturer': 'GILEAD SCIENCES INC.', 'exp_date': '2027-05-31', 'region': 'SOUTH ASIA'},
    {'batch_id': 'MRNA-SPI99', 'medicine_name': 'SPIKEVAX (COVID-19 VACCINE mRNA)', 'manufacturer': 'MODERNA INC.', 'exp_date': '2026-08-31', 'region': 'WESTERN ASIA'},
    {'batch_id': 'MRNA-BST11', 'medicine_name': 'MODERNA COVID-19 BOOSTER SHOT', 'manufacturer': 'MODERNA INC.', 'exp_date': '2027-01-31', 'region': 'NORTH AMERICA'},
    {'batch_id': 'BIIB-TEC88', 'medicine_name': 'TECFIDERA (DIMETHYL FUMARATE CAPSULES)', 'manufacturer': 'BIOGEN INC.', 'exp_date': '2027-01-31', 'region': 'EUROPE'},
    {'batch_id': 'BIIB-AVO22', 'medicine_name': 'AVONEX (INTERFERON BETA-1A INJECTION)', 'manufacturer': 'BIOGEN INC.', 'exp_date': '2027-06-30', 'region': 'EAST ASIA'},
    {'batch_id': 'REGN-DUP77', 'medicine_name': 'DUPIXENT (DUPILUMAB INJECTION)', 'manufacturer': 'REGENERON PHARMACEUTICALS', 'exp_date': '2027-03-31', 'region': 'LATIN AMERICA'},
    {'batch_id': 'REGN-EYL88', 'medicine_name': 'EYLEA (AFLIBERCEPT INJECTION)', 'manufacturer': 'REGENERON PHARMACEUTICALS', 'exp_date': '2026-11-30', 'region': 'MIDDLE EAST'},
    {'batch_id': 'VRTX-TRI66', 'medicine_name': 'TRIKAFTA (ELEXACAFTOR + TEZACAFTOR)', 'manufacturer': 'VERTEX PHARMACEUTICALS', 'exp_date': '2027-05-31', 'region': 'UNITED STATES'},
    {'batch_id': 'VRTX-ORK77', 'medicine_name': 'ORKAMBI (LUMACAFTOR + IVACAFTOR)', 'manufacturer': 'VERTEX PHARMACEUTICALS', 'exp_date': '2027-08-31', 'region': 'EUROPEAN UNION'},
    {'batch_id': 'VTRS-VIA55', 'medicine_name': 'VIAGRA (SILDENAFIL CITRATE TABLETS)', 'manufacturer': 'VIATRIS INC.', 'exp_date': '2026-11-30', 'region': 'SOUTH ASIA'},
    {'batch_id': 'VTRS-EPI66', 'medicine_name': 'EPIPEN (EPINEPHRINE INJECTION)', 'manufacturer': 'VIATRIS INC.', 'exp_date': '2027-03-31', 'region': 'NORTH AMERICA'},
    {'batch_id': 'ALXN-SOL44', 'medicine_name': 'SOLIRIS (ECULIZUMAB INJECTION)', 'manufacturer': 'ALEXION PHARMACEUTICALS', 'exp_date': '2026-07-31', 'region': 'WESTERN ASIA'},
    {'batch_id': 'ALXN-ULT55', 'medicine_name': 'ULTOMIRIS (RAVULIZUMAB INJECTION)', 'manufacturer': 'ALEXION PHARMACEUTICALS', 'exp_date': '2027-09-30', 'region': 'EUROPE'},
    {'batch_id': 'INCY-JAK33', 'medicine_name': 'JAKAFI (RUXOLITINIB TABLETS)', 'manufacturer': 'INCYTE CORPORATION', 'exp_date': '2027-02-28', 'region': 'EAST ASIA'},
    {'batch_id': 'INCY-OPZ44', 'medicine_name': 'OPZELURA (RUXOLITINIB CREAM)', 'manufacturer': 'INCYTE CORPORATION', 'exp_date': '2027-10-31', 'region': 'LATIN AMERICA'},
    {'batch_id': 'BMRN-ALD22', 'medicine_name': 'ALDURZYME (LARONIDASE INJECTION)', 'manufacturer': 'BIOMARIN PHARMACEUTICAL', 'exp_date': '2026-06-30', 'region': 'MIDDLE EAST'},
    {'batch_id': 'BMRN-VOX33', 'medicine_name': 'VOXZOGO (VOSORITIDE FOR INJECTION)', 'manufacturer': 'BIOMARIN PHARMACEUTICAL', 'exp_date': '2027-11-30', 'region': 'UNITED STATES'},
    {'batch_id': 'SGEN-ADC11', 'medicine_name': 'ADCETRIS (BRENTUXIMAB VEDOTIN)', 'manufacturer': 'SEAGEN INC.', 'exp_date': '2026-09-30', 'region': 'EUROPEAN UNION'},
    {'batch_id': 'SGEN-PAD22', 'medicine_name': 'PADCEV (ENFORTUMAB VEDOTIN FOR INJECTION)', 'manufacturer': 'SEAGEN INC.', 'exp_date': '2027-05-31', 'region': 'EAST ASIA'},
    {'batch_id': 'ORGAN-NEX99', 'medicine_name': 'NEXPLANON (ETONOGESTREL IMPLANT)', 'manufacturer': 'ORGANON & CO.', 'exp_date': '2027-04-30', 'region': 'LATIN AMERICA'},
    {'batch_id': 'ORGAN-NUV11', 'medicine_name': 'NUVARING (ETONOGESTREL DIARY)', 'manufacturer': 'ORGANON & CO.', 'exp_date': '2027-12-31', 'region': 'SOUTH ASIA'},
    {'batch_id': 'JAZZ-XYR88', 'medicine_name': 'XYREM (SODIUM OXYBATE ORAL SOLUTION)', 'manufacturer': 'JAZZ PHARMACEUTICALS', 'exp_date': '2027-06-30', 'region': 'MIDDLE EAST'},
    {'batch_id': 'JAZZ-EPI99', 'medicine_name': 'EPIDIOLEX (CANNABIDIOL ORAL SOLUTION)', 'manufacturer': 'JAZZ PHARMACEUTICALS', 'exp_date': '2027-08-31', 'region': 'NORTH AMERICA'},
    {'batch_id': 'HRZN-TEP77', 'medicine_name': 'TEPEZZA (TEPROTUMUMAB INJECTION)', 'manufacturer': 'HORIZON THERAPEUTICS', 'exp_date': '2026-10-31', 'region': 'WESTERN ASIA'},
    {'batch_id': 'HRZN-KRY88', 'medicine_name': 'KRYSTEXXA (PEGLOTICASE INJECTION)', 'manufacturer': 'HORIZON THERAPEUTICS', 'exp_date': '2027-07-31', 'region': 'EUROPE'},
    # 5 Pending US (10 medicines)
    {'batch_id': 'JNJ-TYL77', 'medicine_name': 'TYLENOL (ACETAMINOPHEN TABLETS)', 'manufacturer': 'JOHNSON & JOHNSON', 'exp_date': '2027-05-31', 'region': 'UNITED STATES'},
    {'batch_id': 'JNJ-REM88', 'medicine_name': 'REMICADE (INFLIXIMAB INJECTION)', 'manufacturer': 'JOHNSON & JOHNSON', 'exp_date': '2027-09-30', 'region': 'EUROPEAN UNION'},
    {'batch_id': 'MERK-KEY66', 'medicine_name': 'KEYTRUDA (PEMBROLIZUMAB INJECTION)', 'manufacturer': 'MERCK & CO. INC.', 'exp_date': '2027-04-30', 'region': 'EAST ASIA'},
    {'batch_id': 'MERK-SIN77', 'medicine_name': 'SINGULAIR (MONTELUKAST SODIUM)', 'manufacturer': 'MERCK & CO. INC.', 'exp_date': '2027-10-31', 'region': 'SOUTH ASIA'},
    {'batch_id': 'ABBV-HUM55', 'medicine_name': 'HUMIRA (ADALIMUMAB INJECTION)', 'manufacturer': 'ABBVIE INC.', 'exp_date': '2026-12-31', 'region': 'LATIN AMERICA'},
    {'batch_id': 'ABBV-IMB66', 'medicine_name': 'IMBRUVICA (IBRUTINIB CAPSULES)', 'manufacturer': 'ABBVIE INC.', 'exp_date': '2027-11-30', 'region': 'MIDDLE EAST'},
    {'batch_id': 'BMS-ELI44', 'medicine_name': 'ELIQUIS (APIXABAN TABLETS)', 'manufacturer': 'BRISTOL MYERS SQUIBB', 'exp_date': '2026-11-30', 'region': 'NORTH AMERICA'},
    {'batch_id': 'BMS-OPD55', 'medicine_name': 'OPDIVO (NIVOLUMAB INJECTION)', 'manufacturer': 'BRISTOL MYERS SQUIBB', 'exp_date': '2027-12-31', 'region': 'WESTERN ASIA'},
    {'batch_id': 'LILLY-PRO33', 'medicine_name': 'PROZAC (FLUOXETINE CAPSULES)', 'manufacturer': 'ELI LILLY AND COMPANY', 'exp_date': '2027-03-31', 'region': 'EUROPE'},
    {'batch_id': 'LILLY-HUM44', 'medicine_name': 'HUMALOG (INSULIN LISPRO INJECTION)', 'manufacturer': 'ELI LILLY AND COMPANY', 'exp_date': '2027-09-30', 'region': 'EAST ASIA'},
    # 10 New US Companies (20 medicines)
    {'batch_id': 'BAX-DIA11', 'medicine_name': 'DIANEAL (PERITONEAL DIALYSIS SOLUTION)', 'manufacturer': 'BAXTER INTERNATIONAL INC.', 'exp_date': '2026-08-31', 'region': 'UNITED STATES'},
    {'batch_id': 'BAX-FLE22', 'medicine_name': 'FLEXBUMIN (HUMAN ALBUMIN INJECTION)', 'manufacturer': 'BAXTER INTERNATIONAL INC.', 'exp_date': '2027-06-30', 'region': 'EUROPEAN UNION'},
    {'batch_id': 'ALK-VIV33', 'medicine_name': 'VIVITROL (NALTREXONE EXTENDED RELEASE)', 'manufacturer': 'ALKERMES PLC', 'exp_date': '2027-03-31', 'region': 'NORTH AMERICA'},
    {'batch_id': 'ALK-ARI44', 'medicine_name': 'ARISTADA (ARIPIPRAZOLE LAUROXIL)', 'manufacturer': 'ALKERMES PLC', 'exp_date': '2027-09-30', 'region': 'EAST ASIA'},
    {'batch_id': 'MYL-ATO55', 'medicine_name': 'MYLAN-ATORVASTATIN (CHOLESTEROL TABLETS)', 'manufacturer': 'MYLAN PHARMACEUTICALS', 'exp_date': '2026-11-30', 'region': 'LATIN AMERICA'},
    {'batch_id': 'MYL-AML66', 'medicine_name': 'MYLAN-AMLODIPINE (HYPERTENSION TABLETS)', 'manufacturer': 'MYLAN PHARMACEUTICALS', 'exp_date': '2027-08-31', 'region': 'SOUTH ASIA'},
    {'batch_id': 'SAN-LAN77', 'medicine_name': 'LANTUS (INSULIN GLARGINE INJECTION)', 'manufacturer': 'SANOFI US SERVICES', 'exp_date': '2026-10-31', 'region': 'EUROPE'},
    {'batch_id': 'SAN-TOU88', 'medicine_name': 'TOUJEO (INSULIN GLARGINE U-300)', 'manufacturer': 'SANOFI US SERVICES', 'exp_date': '2027-05-31', 'region': 'NORTH AMERICA'},
    {'batch_id': 'GSK-ADV99', 'medicine_name': 'ADVAIR DISKUS (FLUTICASONE + SALMETEROL)', 'manufacturer': 'GLAXOSMITHKLINE US', 'exp_date': '2027-02-28', 'region': 'UNITED STATES'},
    {'batch_id': 'GSK-VEN11', 'medicine_name': 'VENTOLIN HFA (ALBUTEROL INHALER)', 'manufacturer': 'GLAXOSMITHKLINE US', 'exp_date': '2027-09-30', 'region': 'LATIN AMERICA'},
    {'batch_id': 'NOV-ENT22', 'medicine_name': 'ENTRESTO (SACUBITRIL + VALSARTAN)', 'manufacturer': 'NOVARTIS PHARMA US', 'exp_date': '2026-12-31', 'region': 'EUROPEAN UNION'},
    {'batch_id': 'NOV-COS33', 'medicine_name': 'COSENTYX (SECUKINUMAB INJECTION)', 'manufacturer': 'NOVARTIS PHARMA US', 'exp_date': '2027-11-30', 'region': 'MIDDLE EAST'},
    {'batch_id': 'MSD-GAR44', 'medicine_name': 'GARDASIL 9 (HPV VACCINE RECOMBINANT)', 'manufacturer': 'MERCK SHARP & DOHME', 'exp_date': '2027-04-30', 'region': 'EAST ASIA'},
    {'batch_id': 'MSD-JAN55', 'medicine_name': 'JANUVIA (SITAGLIPTIN DIABETES TABLETS)', 'manufacturer': 'MERCK SHARP & DOHME', 'exp_date': '2027-10-31', 'region': 'WESTERN ASIA'},
    {'batch_id': 'AZ-CRE66', 'medicine_name': 'CRESTOR (ROSUVASTATIN CALCIUM)', 'manufacturer': 'ASTRAZENECA US', 'exp_date': '2026-11-30', 'region': 'UNITED STATES'},
    {'batch_id': 'AZ-SYM77', 'medicine_name': 'SYMBICORT (BUDESONIDE + FORMOTEROL)', 'manufacturer': 'ASTRAZENECA US', 'exp_date': '2027-08-31', 'region': 'SOUTH ASIA'},
    {'batch_id': 'TAK-VYV88', 'medicine_name': 'VYVANSE (LISDEXAMFETAMINE CAPSULES)', 'manufacturer': 'TAKEDA PHARMACEUTICALS US', 'exp_date': '2027-03-31', 'region': 'NORTH AMERICA'},
    {'batch_id': 'TAK-ENT99', 'medicine_name': 'ENTYVIO (VEDOLIZUMAB INJECTION)', 'manufacturer': 'TAKEDA PHARMACEUTICALS US', 'exp_date': '2027-12-31', 'region': 'EUROPE'},
    {'batch_id': 'BI-JAR11', 'medicine_name': 'JARDIANCE (EMPAGLIFLOZIN TABLETS)', 'manufacturer': 'BOEHRINGER INGELHEIM US', 'exp_date': '2026-10-31', 'region': 'LATIN AMERICA'},
    {'batch_id': 'BI-SPI22', 'medicine_name': 'SPIRIVA HANDIHALER (TIOTROPIUM)', 'manufacturer': 'BOEHRINGER INGELHEIM US', 'exp_date': '2027-09-30', 'region': 'EAST ASIA'},

    # 20 Indian Approved (40 medicines)
    {'batch_id': 'GSD0144A', 'medicine_name': 'ROSUVAS 10 (ROSUVASTATIN CALCIUM 10MG TABLETS)', 'manufacturer': 'SUN PHARMACEUTICAL INDUSTRIES LTD.', 'exp_date': '2026-12-31', 'region': 'DOMESTIC'},
    {'batch_id': 'GSD0155B', 'medicine_name': 'VOLINI (DICLOFENAC PAIN RELIEF GEL)', 'manufacturer': 'SUN PHARMACEUTICAL INDUSTRIES LTD.', 'exp_date': '2027-05-31', 'region': 'SOUTH ASIA'},
    {'batch_id': 'BTD9045B', 'medicine_name': 'OMEZ 20 (OMEPRAZOLE 20MG CAPSULES)', 'manufacturer': 'DR. REDDYS LABORATORIES LTD.', 'exp_date': '2026-11-30', 'region': 'DOMESTIC'},
    {'batch_id': 'BTD9056C', 'medicine_name': 'NISE (NIMESULIDE ACUTE PAIN TABLETS)', 'manufacturer': 'DR. REDDYS LABORATORIES LTD.', 'exp_date': '2027-06-30', 'region': 'LATIN AMERICA'},
    {'batch_id': 'LJD8834C', 'medicine_name': 'GLUCONORM-G1 FORTE (GLIMEPIRIDE 1MG + METFORMIN 1000MG)', 'manufacturer': 'LUPIN LIMITED', 'exp_date': '2027-01-31', 'region': 'DOMESTIC'},
    {'batch_id': 'LJD8845D', 'medicine_name': 'LUPISULIN (HUMAN INSULIN SUSPENSION)', 'manufacturer': 'LUPIN LIMITED', 'exp_date': '2027-08-31', 'region': 'MIDDLE EAST'},
    {'batch_id': 'MKD7721D', 'medicine_name': 'NUROKIND-LC (METHYLCOBALAMIN + L-CARNITINE TABLETS)', 'manufacturer': 'MANKIND PHARMA LTD.', 'exp_date': '2026-10-31', 'region': 'DOMESTIC'},
    {'batch_id': 'MKD7732E', 'medicine_name': 'MANFORCE (SILDENAFIL CITRATE TABLETS)', 'manufacturer': 'MANKIND PHARMA LTD.', 'exp_date': '2027-09-30', 'region': 'SOUTH ASIA'},
    {'batch_id': 'PFD6612E', 'medicine_name': 'BECOSULES CAPSULES (VITAMIN B-COMPLEX + VITAMIN C)', 'manufacturer': 'PFIZER LIMITED', 'exp_date': '2027-05-31', 'region': 'DOMESTIC'},
    {'batch_id': 'PFD6623F', 'medicine_name': 'COREX (COUGH SYRUP FORMULATION)', 'manufacturer': 'PFIZER LIMITED', 'exp_date': '2027-10-31', 'region': 'WESTERN ASIA'},
    {'batch_id': 'GF244009', 'medicine_name': 'RUBIRED Z', 'manufacturer': 'MACLEODS PHARMACEUTICALS LTD.', 'exp_date': '2026-06-30', 'region': 'DOMESTIC'},
    {'batch_id': 'GF244010', 'medicine_name': 'MACFOLATE (FOLIC ACID SUPPLEMENT)', 'manufacturer': 'MACLEODS PHARMACEUTICALS LTD.', 'exp_date': '2027-11-30', 'region': 'EAST ASIA'},
    {'batch_id': 'INC2570', 'medicine_name': 'MEGAFERON', 'manufacturer': 'ARISTO PHARMACEUTICALS', 'exp_date': '2026-12-01', 'region': 'DOMESTIC'},
    {'batch_id': 'INC2581', 'medicine_name': 'ARISTOFOL (PREMIUM MULTIVITAMIN)', 'manufacturer': 'ARISTO PHARMACEUTICALS', 'exp_date': '2027-12-31', 'region': 'EUROPE'},
    {'batch_id': 'REX9900', 'medicine_name': 'REXCOF DX COUGH SYRUP', 'manufacturer': 'CIPLA LIMITED', 'exp_date': '2026-10-31', 'region': 'DOMESTIC'},
    {'batch_id': 'REX9911', 'medicine_name': 'CIPLOX (CIPROFLOXACIN TABLETS)', 'manufacturer': 'CIPLA LIMITED', 'exp_date': '2027-05-31', 'region': 'EUROPEAN UNION'},
    {'batch_id': 'TOR5566A', 'medicine_name': 'CHYMORAL FORTE (TRYPSIN-CHYMOTRYPSIN TABLETS)', 'manufacturer': 'TORRENT PHARMACEUTICALS LTD.', 'exp_date': '2026-10-31', 'region': 'DOMESTIC'},
    {'batch_id': 'TOR5577B', 'medicine_name': 'AZULIX (GLIMEPIRIDE TABLETS)', 'manufacturer': 'TORRENT PHARMACEUTICALS LTD.', 'exp_date': '2027-07-31', 'region': 'NORTH AMERICA'},
    {'batch_id': 'GLN4433B', 'medicine_name': 'ASCORIL LS SYRUP (AMBROXOL + LEVOSALBUTAMOL)', 'manufacturer': 'GLENMARK PHARMACEUTICALS LTD.', 'exp_date': '2026-09-30', 'region': 'DOMESTIC'},
    {'batch_id': 'GLN4444C', 'medicine_name': 'TELMA 40 (TELMISARTAN HYPERTENSION TABLETS)', 'manufacturer': 'GLENMARK PHARMACEUTICALS LTD.', 'exp_date': '2027-08-31', 'region': 'EAST ASIA'},
    {'batch_id': 'ALK1122C', 'medicine_name': 'CLAVAM 625 (AMOXICILLIN + POTASSIUM CLAVULANATE)', 'manufacturer': 'ALKEM LABORATORIES LTD.', 'exp_date': '2026-12-31', 'region': 'DOMESTIC'},
    {'batch_id': 'ALK1133D', 'medicine_name': 'PAN-D (PANTOPRAZOLE + DOMPERIDONE)', 'manufacturer': 'ALKEM LABORATORIES LTD.', 'exp_date': '2027-09-30', 'region': 'LATIN AMERICA'},
    {'batch_id': 'ZYD9988D', 'medicine_name': 'LIPAGLYN (SAROGLITAZAR TABLETS)', 'manufacturer': 'ZYDUS LIFESCIENCES LTD.', 'exp_date': '2027-02-28', 'region': 'DOMESTIC'},
    {'batch_id': 'ZYD9999E', 'medicine_name': 'ZYCLAV (AMOXICILLIN FOR SUSPENSION)', 'manufacturer': 'ZYDUS LIFESCIENCES LTD.', 'exp_date': '2027-10-31', 'region': 'MIDDLE EAST'},
    {'batch_id': 'BIO7766E', 'medicine_name': 'INSUGEN (HUMAN INSULIN INJECTION)', 'manufacturer': 'BIOCON LIMITED', 'exp_date': '2026-08-31', 'region': 'DOMESTIC'},
    {'batch_id': 'BIO7777F', 'medicine_name': 'CANMAB (TRASTUZUMAB TARGETED INJECTION)', 'manufacturer': 'BIOCON LIMITED', 'exp_date': '2027-11-30', 'region': 'UNITED STATES'},
    {'batch_id': 'INT5544F', 'medicine_name': 'LIPICARD 160 (FENOFIBRATE TABLETS)', 'manufacturer': 'INTAS PHARMACEUTICALS LTD.', 'exp_date': '2026-11-30', 'region': 'DOMESTIC'},
    {'batch_id': 'INT5555G', 'medicine_name': 'INTACEF (CEFTRIAXONE ANTIBIOTIC INJECTION)', 'manufacturer': 'INTAS PHARMACEUTICALS LTD.', 'exp_date': '2027-12-31', 'region': 'EUROPE'},
    {'batch_id': 'AUR3322G', 'medicine_name': 'AMLOSAFE 5 (AMLODIPINE TABLETS)', 'manufacturer': 'AUROBINDO PHARMA LTD.', 'exp_date': '2027-01-31', 'region': 'DOMESTIC'},
    {'batch_id': 'AUR3333H', 'medicine_name': 'AURO-AZITHROMYCIN (ANTIBIOTIC TABLETS)', 'manufacturer': 'AUROBINDO PHARMA LTD.', 'exp_date': '2027-05-31', 'region': 'EUROPEAN UNION'},
    {'batch_id': 'IPC1199H', 'medicine_name': 'LARIAGO 250 (CHLOROQUINE PHOSPHATE TABLETS)', 'manufacturer': 'IPCA LABORATORIES LTD.', 'exp_date': '2026-07-31', 'region': 'DOMESTIC'},
    {'batch_id': 'IPC1188I', 'medicine_name': 'ZERO-DOL SP (ACECLOFENAC COMBINATION)', 'manufacturer': 'IPCA LABORATORIES LTD.', 'exp_date': '2027-06-30', 'region': 'LATIN AMERICA'},
    {'batch_id': 'ALM8877I', 'medicine_name': 'AZITHRAL 500 (AZITHROMYCIN TABLETS)', 'manufacturer': 'ALEMBIC PHARMACEUTICALS LTD.', 'exp_date': '2026-12-31', 'region': 'DOMESTIC'},
    {'batch_id': 'ALM8888J', 'medicine_name': 'ALERID (CETIRIZINE ALLERGY TABLETS)', 'manufacturer': 'ALEMBIC PHARMACEUTICALS LTD.', 'exp_date': '2027-08-31', 'region': 'MIDDLE EAST'},
    {'batch_id': 'ABB6655J', 'medicine_name': 'THYRONORM (LEVOTHYROXINE SODIUM TABLETS)', 'manufacturer': 'ABBOTT INDIA LIMITED', 'exp_date': '2027-04-30', 'region': 'DOMESTIC'},
    {'batch_id': 'ABB6666K', 'medicine_name': 'DUPHASTON (DYDROGESTERONE TABLETS)', 'manufacturer': 'ABBOTT INDIA LIMITED', 'exp_date': '2027-09-30', 'region': 'SOUTH ASIA'},
    {'batch_id': 'GSK4433K', 'medicine_name': 'AUGMENTIN 625 DUO (AMOXICILLIN + CLAVULANATE)', 'manufacturer': 'GLAXOSMITHKLINE PHARMACEUTICALS', 'exp_date': '2026-10-31', 'region': 'DOMESTIC'},
    {'batch_id': 'GSK4444L', 'medicine_name': 'CALPOL 500 (PARACETAMOL HEADACHE TABLETS)', 'manufacturer': 'GLAXOSMITHKLINE PHARMACEUTICALS', 'exp_date': '2027-10-31', 'region': 'UNITED STATES'},
    {'batch_id': 'NOV2211L', 'medicine_name': 'VOVERAN SR 100 (DICLOFENAC SODIUM)', 'manufacturer': 'NOVARTIS INDIA LIMITED', 'exp_date': '2027-03-31', 'region': 'DOMESTIC'},
    {'batch_id': 'NOV2222M', 'medicine_name': 'GALVUS MET (VILDAGLIPTIN + METFORMIN)', 'manufacturer': 'NOVARTIS INDIA LIMITED', 'exp_date': '2027-11-30', 'region': 'EUROPE'},
    # 10 New Indian Approved (20 medicines)
    {'batch_id': 'MIC-DOL11', 'medicine_name': 'DOLO 650 (PARACETAMOL 650MG TABLETS)', 'manufacturer': 'MICRO LABS LIMITED', 'exp_date': '2026-08-31', 'region': 'DOMESTIC'},
    {'batch_id': 'MIC-CAR22', 'medicine_name': 'CARVIPRESS (CARVIPRESS CARVEDILOL)', 'manufacturer': 'MICRO LABS LIMITED', 'exp_date': '2027-06-30', 'region': 'SOUTH ASIA'},
    {'batch_id': 'FDC-ELE33', 'medicine_name': 'ELECTRAL ORS (REHYDRATION SALTS)', 'manufacturer': 'FDC LIMITED', 'exp_date': '2027-03-31', 'region': 'DOMESTIC'},
    {'batch_id': 'FDC-ZEF44', 'medicine_name': 'ZEFI (CEFIXIME ANTIMICROBIAL TABLETS)', 'manufacturer': 'FDC LIMITED', 'exp_date': '2027-09-30', 'region': 'MIDDLE EAST'},
    {'batch_id': 'COR-CAL55', 'medicine_name': 'COROCAL (CALCIUM SUPPLEMENT)', 'manufacturer': 'CORONATION PHARMA', 'exp_date': '2026-11-30', 'region': 'DOMESTIC'},
    {'batch_id': 'COR-PRI66', 'medicine_name': 'COROPRIL (ENALAPRIL HYPERTENSION)', 'manufacturer': 'CORONATION PHARMA', 'exp_date': '2027-08-31', 'region': 'LATIN AMERICA'},
    {'batch_id': 'HET-COV77', 'medicine_name': 'COVIPRI (REMDESIVIR COVIPRI INJECTION)', 'manufacturer': 'HETERO DRUGS LTD', 'exp_date': '2026-10-31', 'region': 'DOMESTIC'},
    {'batch_id': 'HET-LIP88', 'medicine_name': 'HETERO-LIP (ATORVASTATIN GENERIC)', 'manufacturer': 'HETERO DRUGS LTD', 'exp_date': '2027-05-31', 'region': 'EAST ASIA'},
    {'batch_id': 'APO-MET99', 'medicine_name': 'APO-METFORMIN (DIABETES CONTROL CAPSULES)', 'manufacturer': 'APOTEX RESEARCH INDIA', 'exp_date': '2027-02-28', 'region': 'DOMESTIC'},
    {'batch_id': 'APO-ATE11', 'medicine_name': 'APO-ATENOLOL (BETA BLOCKER TABLETS)', 'manufacturer': 'APOTEX RESEARCH INDIA', 'exp_date': '2027-09-30', 'region': 'EUROPE'},
    {'batch_id': 'SUN-REV22', 'medicine_name': 'REVITAL H (DAILY ENERGY MULTIVITAMIN)', 'manufacturer': 'SUN PHARMA LABORATORIES', 'exp_date': '2026-12-31', 'region': 'DOMESTIC'},
    {'batch_id': 'SUN-CHE33', 'medicine_name': 'CHERI SYRUP (IRON AND FOLIC ACID)', 'manufacturer': 'SUN PHARMA LABORATORIES', 'exp_date': '2027-11-30', 'region': 'WESTERN ASIA'},
    {'batch_id': 'BC-TUS44', 'medicine_name': 'TUSQ-D (COUGH AND COLD LIQUID)', 'manufacturer': 'BLUE CROSS LABORATORIES', 'exp_date': '2026-11-30', 'region': 'DOMESTIC'},
    {'batch_id': 'BC-MEF55', 'medicine_name': 'MEFTAL-SPAS (SPASMODIC PAIN RELIEF)', 'manufacturer': 'BLUE CROSS LABORATORIES', 'exp_date': '2027-08-31', 'region': 'SOUTH ASIA'},
    {'batch_id': 'EMC-ORO66', 'medicine_name': 'OROFER-XT (PREMIUM IRON INJECTION)', 'manufacturer': 'EMCURE PHARMACEUTICALS LTD.', 'exp_date': '2027-03-31', 'region': 'DOMESTIC'},
    {'batch_id': 'EMC-MET77', 'medicine_name': 'METAPRO-XL (METOPROLOL CARDIO RES)', 'manufacturer': 'EMCURE PHARMACEUTICALS LTD.', 'exp_date': '2027-12-31', 'region': 'EAST ASIA'},
    {'batch_id': 'AJA-MET88', 'medicine_name': 'METXL (METOPROLOL ANGINA CONTROL)', 'manufacturer': 'AJANTA PHARMA LTD.', 'exp_date': '2027-03-31', 'region': 'DOMESTIC'},
    {'batch_id': 'AJA-MEL99', 'medicine_name': 'MELACARE (SKIN REGENERATION CREAM)', 'manufacturer': 'AJANTA PHARMA LTD.', 'exp_date': '2027-12-31', 'region': 'LATIN AMERICA'},
    {'batch_id': 'MKS-GAS11', 'medicine_name': 'GASP-O (ADVANCED ACIDITY GEL)', 'manufacturer': 'MANKIND SPECIALTIES', 'exp_date': '2026-10-31', 'region': 'DOMESTIC'},
    {'batch_id': 'MKS-MER22', 'medicine_name': 'MERO-TROL (MERO-TROL MEROPENEM)', 'manufacturer': 'MANKIND SPECIALTIES', 'exp_date': '2027-09-30', 'region': 'MIDDLE EAST'}
]

db = SessionLocal()

# 1. Truncate Tables and Restart Sequence Identities to 1
try:
    print("Truncating tables and resetting serial IDs to 1...")
    db.execute(text("TRUNCATE TABLE manufacturers RESTART IDENTITY CASCADE;"))
    db.execute(text("TRUNCATE TABLE medicines RESTART IDENTITY CASCADE;"))
    db.commit()
    print("Truncation successfully restarted identity sequences at 1!")
except Exception as e:
    print(f"Error during truncation: {e}")
    db.rollback()

# 2. Seed Manufacturers starting exactly at ID 1
for c in companies:
    mfg = Manufacturer(
        name=c['name'],
        security_email=c['email'],
        contact_person=c['auth'],
        blockchain_address=c['wallet'],
        status=c['status'],
        email_verified=c['verified'],
        verification_code='555560'
    )
    db.add(mfg)
db.commit()
print("60 Manufacturers successfully seeded starting at ID 1!")

# 3. Seed Medicines starting exactly at ID 1
for m in medicines:
    med = Medicine(
        name=m['medicine_name'].strip().upper(),
        manufacturer=m['manufacturer'].strip().upper()
    )
    db.add(med)
db.commit()
print("120 Medicines successfully seeded starting at ID 1!")

# 4. Save to Mock Ledger File
ledger_dir = os.path.join("data", "brand_templates")
os.makedirs(ledger_dir, exist_ok=True)
ledger_path = os.path.join(ledger_dir, "mock_blockchain_ledger.json")

ledger = {}
for m in medicines:
    mfg_ts = int(datetime.now().timestamp())
    exp_ts = int(datetime.strptime(m['exp_date'], '%Y-%m-%d').timestamp())
    
    ledger[m['batch_id']] = {
        'name': m['medicine_name'],
        'manufacturer': m['manufacturer'],
        'mfg_ts': mfg_ts,
        'exp_ts': exp_ts,
        'expiry_date': m['exp_date'],
        'region': m['region']
    }

with open(ledger_path, 'w', encoding='utf-8') as f:
    json.dump(ledger, f, indent=4)

print("Mock blockchain ledger updated successfully with 120 elements!")
db.close()
