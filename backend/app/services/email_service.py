import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def get_manufacturer_email(manufacturer_name):
    """
    Fetches the security email for a manufacturer from the database in REAL-TIME.
    No hardcoded data.
    """
    from app.db.session import SessionLocal
    from app.models.manufacturer import Manufacturer

    db = SessionLocal()
    try:
        if not manufacturer_name or manufacturer_name == "Unknown":
            return os.getenv("MANUFACTURER_EMAIL")

        # Clean name for searching
        clean_name = str(manufacturer_name).strip().upper()

        # Real-time DB Lookup (Multiple strategies for robustness)
        # Strategy A: Reported name is a substring of Manufacturer Name (e.g. 'CIPLA' -> 'CIPLA LTD')
        mfg = (
            db.query(Manufacturer)
            .filter(Manufacturer.name.ilike(f"%{clean_name}%"))
            .first()
        )

        # Strategy B: Manufacturer Name is part of Reported Name (e.g. 'CIPLA LTD' -> 'CIPLA MEDICINE')
        if not mfg:
            all_mfgs = db.query(Manufacturer).all()
            for m_item in all_mfgs:
                m_base = (
                    m_item.name.upper()
                    .replace(" LTD", "")
                    .replace(" LIMITED", "")
                    .replace("PVT", "")
                    .strip()
                )
                # Check if the core brand name exists in the report name
                if len(m_base) > 2 and (m_base in clean_name or clean_name in m_base):
                    mfg = m_item
                    break

        if mfg and mfg.security_email:
            print(
                f"📊 Real-time Routing: Found email for {clean_name} -> {mfg.security_email}"
            )
            return mfg.security_email

        # Fallback to system default if not in DB
        return os.getenv("MANUFACTURER_EMAIL")
    except Exception as e:
        print(f"⚠ DB lookup for manufacturer failed: {e}")
        return os.getenv("MANUFACTURER_EMAIL")
    finally:
        db.close()


def send_security_alert(report_data):
    """
    Sends a professional security alert email to the manufacturer.
    """
    mail_username = os.getenv("MAIL_USERNAME")
    mail_password = os.getenv("MAIL_PASSWORD")
    mail_server = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    mail_port = int(os.getenv("MAIL_PORT", 587))
    from_name = os.getenv("MAIL_FROM_NAME", "MedScan-AI Security Hub")

    # REAL-TIME DYNAMIC ROUTING
    # 1. Fetch the scan associated with this report to get the ACTUAL manufacturer
    from app.db.session import SessionLocal
    from app.models.scan import Scan

    manufacturer_found = None
    db_lookup = SessionLocal()
    try:
        if report_data.scan_id:
            related_scan = (
                db_lookup.query(Scan).filter(Scan.id == report_data.scan_id).first()
            )
            if related_scan and related_scan.manufacturer:
                manufacturer_found = related_scan.manufacturer
    except Exception as e:
        print(f"Error tracing manufacturer for report: {e}")
    finally:
        db_lookup.close()

    # 2. Get the specific security email for that manufacturer
    # This will use get_manufacturer_email which searches the database
    # Passing the found manufacturer name (e.g. 'CIPLA LTD')
    # instead of the medicine name ('TETRACYCLINE')
    manufacturer_email = get_manufacturer_email(
        manufacturer_found or report_data.medicine_name
    )

    if not all([mail_username, mail_password, manufacturer_email]):
        print(
            "⚠ Email credentials or manufacturer email not configured. Skipping alert."
        )
        return

    # 🚨 SECURITY ALERT Subject
    subject = f"🚨 SECURITY ALERT: {report_data.issue_type} Detected for Batch #{report_data.batch_id}"

    # Email Body (HTML Template)
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
            <h2 style="color: #dc3545; border-bottom: 2px solid #dc3545; padding-bottom: 10px;">
                MedScan-AI Global Security Alert
            </h2>
            <p style="font-weight: bold; color: #dc3545;">System Identification: MedScan-AI Global Security Network</p>
            <p style="font-weight: bold;">Priority: <span style="color: #dc3545;">HIGH (Critical Risk)</span></p>

            <h3 style="background-color: #343a40; color: #fff; padding: 5px 10px; border-radius: 5px;">1. Medicine Context</h3>
            <ul style="list-style: none; padding-left: 0;">
                <li><strong>Medicine Name:</strong> {report_data.medicine_name}</li>
                <li><strong>Batch Number:</strong> {report_data.batch_id}</li>
                <li><strong>Manufacturer Registered:</strong> Automated Registry Trace</li>
            </ul>

            <h3 style="background-color: #343a40; color: #fff; padding: 5px 10px; border-radius: 5px;">2. Incident Assessment</h3>
            <ul style="list-style: none; padding-left: 0;">
                <li><strong>Observed Issue:</strong> <span style="color: #dc3545; font-weight: bold;">{report_data.issue_type}</span></li>
                <li><strong>Source of Report:</strong> End-User Forensic App</li>
            </ul>

            <h3 style="background-color: #343a40; color: #fff; padding: 5px 10px; border-radius: 5px;">3. Precise Location (Geospatial Data)</h3>
            <ul style="list-style: none; padding-left: 0;">
                <li><strong>Pharmacy/Purchase Point:</strong> {report_data.location_details}</li>
                <li><strong>GPS Coordinates:</strong> {report_data.lat}, {report_data.lng}</li>
                <li><strong>Live Map Link:</strong> <a href="https://www.google.com/maps?q={report_data.lat},{report_data.lng}" style="color: #007bff;">View Location on Google Maps</a></li>
            </ul>

            <h3 style="background-color: #343a40; color: #fff; padding: 5px 10px; border-radius: 5px;">4. Forensic Description</h3>
            <p style="background-color: #fff; border-left: 5px solid #007bff; padding: 10px; font-style: italic;">
                "{report_data.description}"
            </p>

            <h3 style="background-color: #28a745; color: #fff; padding: 5px 10px; border-radius: 5px;">5. Recommendation</h3>
            <p>Please cross-verify this Batch ID in the Blockchain Registry. If this is a suspected counterfeit, immediate investigation at the purchase point is recommended.</p>
            
            <hr style="border: 0; border-top: 1px solid #ccc; margin: 20px 0;">
            <p style="font-size: 12px; color: #6c757d; text-align: center;">
                This is an automated security alert generated by MedScan-AI Real-Time Forensics.
            </p>
        </div>
    </body>
    </html>
    """

    # Setup Message
    msg = MIMEMultipart()
    msg["From"] = f"{from_name} <{mail_username}>"
    msg["To"] = manufacturer_email
    msg["Subject"] = subject
    msg.attach(MIMEText(html_content, "html"))

    try:
        # Connect and Send
        server = smtplib.SMTP(mail_server, mail_port)
        server.starttls()  # Secure Connection
        server.login(mail_username, mail_password)
        server.send_message(msg)
        server.quit()
        print(f"✅ Security Alert sent successfully to {manufacturer_email}")
    except Exception as e:
        print(f"❌ Failed to send security alert: {e}")


def send_outbreak_alert(outbreak_data):
    """
    Sends a CRITICAL regional outbreak alert for detected clone attacks.
    """
    mail_username = os.getenv("MAIL_USERNAME")
    mail_password = os.getenv("MAIL_PASSWORD")
    mail_server = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    mail_port = int(os.getenv("MAIL_PORT", 587))

    # REAL-TIME DYNAMIC ROUTING FOR OUTBREAKS
    mfg_name = (
        outbreak_data["medicine_names"][0]
        if outbreak_data["medicine_names"]
        else "Unknown"
    )
    manufacturer_email = get_manufacturer_email(mfg_name)

    if not all([mail_username, mail_password, manufacturer_email]):
        print("⚠ Email config missing. Skipping outbreak alert.")
        return

    subject = f"🚨 CRITICAL: Regional Clone Attack Detected - {outbreak_data['scan_count']} Scans Found!"

    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="background-color: #721c24; color: #fff; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
            <h1>🚨 REGIONAL OUTBREAK DETECTED</h1>
        </div>
        <div style="border: 2px solid #721c24; padding: 20px; border-radius: 0 0 10px 10px;">
            <h2 style="color: #721c24;">AI Cluster Analysis Report</h2>
            <p>Our AI-powered clustering algorithm has identified a <strong>concentrated injection</strong> of suspicious medicines in a specific area.</p>
            
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <tr style="background-color: #f8d7da;">
                    <td style="padding: 10px; border: 1px solid #dee2e6;"><strong>Severity:</strong></td>
                    <td style="padding: 10px; border: 1px solid #dee2e6; color: #721c24; font-weight: bold;">{outbreak_data['severity']}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #dee2e6;"><strong>Total Scans:</strong></td>
                    <td style="padding: 10px; border: 1px solid #dee2e6;">{outbreak_data['scan_count']}</td>
                </tr>
                <tr style="background-color: #f8f9fa;">
                    <td style="padding: 10px; border: 1px solid #dee2e6;"><strong>Radius:</strong></td>
                    <td style="padding: 10px; border: 1px solid #dee2e6;">{outbreak_data['radius_km']} KM</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #dee2e6;"><strong>Medicine Clusters:</strong></td>
                    <td style="padding: 10px; border: 1px solid #dee2e6;">{", ".join(outbreak_data['medicine_names'])}</td>
                </tr>
                <tr style="background-color: #f8f9fa;">
                    <td style="padding: 10px; border: 1px solid #dee2e6;"><strong>Batch IDs Involved:</strong></td>
                    <td style="padding: 10px; border: 1px solid #dee2e6;">{", ".join(outbreak_data['batch_ids'])}</td>
                </tr>
            </table>

            <h3 style="color: #004085; border-bottom: 2px solid #004085;">Recommended Action</h3>
            <p>1. Immediate <strong>Regional Recall</strong> of mentioned Batches for the affected area.<br>
            2. Field team investigation at GPS: <strong>{outbreak_data['lat']}, {outbreak_data['lng']}</strong>.<br>
            3. Alert local drug control authorities.</p>

            <div style="text-align: center; margin-top: 30px;">
                <a href="https://www.google.com/maps?q={outbreak_data['lat']},{outbreak_data['lng']}" 
                   style="background-color: #dc3545; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                   VIEW REGIONAL HEATMAP
                </a>
            </div>
        </div>
        <p style="font-size: 11px; color: #666; text-align: center; margin-top: 20px;">
            Powered by MedScan-AI Geospatial Analytics Dashboard.
        </p>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg["From"] = f"MedScan-AI Security Hub <{mail_username}>"
    msg["To"] = manufacturer_email
    msg["Subject"] = subject
    msg.attach(MIMEText(html_content, "html"))

    try:
        server = smtplib.SMTP(mail_server, mail_port)
        server.starttls()
        server.login(mail_username, mail_password)
        server.send_message(msg)
        server.quit()
        print(f"🔥 CRITICAL OUTBREAK ALERT SENT to {manufacturer_email}")
    except Exception as e:
        print(f"❌ Failed to send outbreak alert: {e}")
