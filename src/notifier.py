import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from src import config

def send_email_report(matched_jobs):
    """
    Sends an HTML report of matched jobs to the user's email.
    """
    if not config.SENDER_EMAIL or not config.SENDER_PASSWORD or not config.RECEIVER_EMAIL:
        print("Skipping Email Notification: SMTP Credentials or Receiver Email not configured in environment variables.")
        print(f"Total matched jobs computed: {len(matched_jobs)}")
        return False

    # Count profiles
    ds_count = sum(1 for j in matched_jobs if j['match_info']['best_match'] == 'Data Science')
    da_count = sum(1 for j in matched_jobs if j['match_info']['best_match'] == 'Data Analyst')

    # Build HTML table rows
    table_rows = ""
    for idx, job in enumerate(matched_jobs):
        score = job['match_info']['score']
        best_match = job['match_info']['best_match']
        missing = job['match_info']['missing_keywords']
        
        # Color badge depending on match score
        if score >= 80:
            badge_color = "#10B981"  # Emerald Green
            badge_bg = "#ECFDF5"
        elif score >= 50:
            badge_color = "#F59E0B"  # Amber Orange
            badge_bg = "#FFFBEB"
        else:
            badge_color = "#EF4444"  # Red
            badge_bg = "#FEF2F2"

        # Missing keywords display
        if missing:
            missing_html = ", ".join([f"<span style='background-color:#F3F4F6; color:#4B5563; padding: 2px 6px; border-radius: 4px; font-size: 11px; margin-right: 4px; display: inline-block;'>{kw}</span>" for kw in missing[:8]])
            if len(missing) > 8:
                missing_html += f" <span style='font-size: 11px; color: #9CA3AF;'>+{len(missing)-8} more</span>"
        else:
            missing_html = "<span style='color: #10B981; font-weight: 500;'>Perfect Match! (No missing key skills)</span>"

        table_rows += f"""
        <tr style="border-bottom: 1px solid #E5E7EB;">
            <td style="padding: 12px 15px; font-weight: 500;">
                <a href="{job['link']}" target="_blank" style="color: #2563EB; text-decoration: none; hover: underline;">{job['title']}</a>
            </td>
            <td style="padding: 12px 15px; color: #374151;">{job['company']}</td>
            <td style="padding: 12px 15px; color: #6B7280; font-size: 13px;">{job['location']}</td>
            <td style="padding: 12px 15px; text-align: center;">
                <span style="background-color: {badge_bg}; color: {badge_color}; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; display: inline-block;">
                    {score}%
                </span>
            </td>
            <td style="padding: 12px 15px; text-align: center; color: #1F2937; font-weight: 500; font-size: 13px;">
                {best_match}
            </td>
            <td style="padding: 12px 15px; font-size: 12px; max-width: 250px;">
                {missing_html}
            </td>
        </tr>
        """

    if not table_rows:
        table_rows = """
        <tr>
            <td colspan="6" style="padding: 30px; text-align: center; color: #6B7280; font-style: italic;">
                No jobs found matching your threshold score of config.MATCH_THRESHOLD%.
            </td>
        </tr>
        """

    # Build full HTML Template
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #F9FAFB;
                margin: 0;
                padding: 0;
                color: #111827;
            }}
            .container {{
                max-width: 900px;
                margin: 20px auto;
                background-color: #FFFFFF;
                border-radius: 12px;
                box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
                overflow: hidden;
                border: 1px solid #E5E7EB;
            }}
            .header {{
                background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
                color: #FFFFFF;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
                font-weight: 700;
                letter-spacing: -0.5px;
            }}
            .header p {{
                margin: 5px 0 0 0;
                opacity: 0.9;
                font-size: 14px;
            }}
            .stats {{
                display: flex;
                justify-content: space-around;
                background-color: #F3F4F6;
                padding: 15px;
                border-bottom: 1px solid #E5E7EB;
            }}
            .stat-box {{
                text-align: center;
            }}
            .stat-val {{
                font-size: 20px;
                font-weight: 700;
                color: #1E3A8A;
            }}
            .stat-lbl {{
                font-size: 12px;
                color: #6B7280;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-top: 2px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            th {{
                background-color: #F9FAFB;
                color: #374151;
                font-weight: 600;
                text-align: left;
                padding: 12px 15px;
                border-bottom: 2px solid #E5E7EB;
                font-size: 13px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .footer {{
                background-color: #F9FAFB;
                padding: 20px;
                text-align: center;
                font-size: 12px;
                color: #9CA3AF;
                border-top: 1px solid #E5E7EB;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Daily Job Matching Report</h1>
                <p>Automated matches based on your Data Science and Data Analyst resumes</p>
            </div>
            
            <!-- Gmail-compatible stats section using tables -->
            <table cellpadding="0" cellspacing="0" style="width: 100%; background-color: #F3F4F6; border-bottom: 1px solid #E5E7EB; padding: 15px; text-align: center;">
                <tr>
                    <td style="width: 33.33%; text-align: center; padding: 10px 0;">
                        <div style="font-size: 22px; font-weight: 700; color: #1E3A8A;">{len(matched_jobs)}</div>
                        <div style="font-size: 11px; color: #6B7280; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 2px;">Total Scanned</div>
                    </td>
                    <td style="width: 33.33%; text-align: center; border-left: 1px solid #E5E7EB; border-right: 1px solid #E5E7EB; padding: 10px 0;">
                        <div style="font-size: 22px; font-weight: 700; color: #10B981;">{ds_count}</div>
                        <div style="font-size: 11px; color: #6B7280; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 2px;">Data Science Matches</div>
                    </td>
                    <td style="width: 33.33%; text-align: center; padding: 10px 0;">
                        <div style="font-size: 22px; font-weight: 700; color: #3B82F6;">{da_count}</div>
                        <div style="font-size: 11px; color: #6B7280; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 2px;">Data Analyst Matches</div>
                    </td>
                </tr>
            </table>
            
            <div style="overflow-x: auto;">
                <table>
                    <thead>
                        <tr>
                            <th>Job Title</th>
                            <th>Company</th>
                            <th>Location</th>
                            <th style="text-align: center;">Match Score</th>
                            <th style="text-align: center;">Target Profile</th>
                            <th>Missing Keywords / Feedback</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </div>
            
            <div class="footer">
                <p>This report was generated automatically. To update keywords or settings, modify the configurations in your script directory.</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Set up email structure
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Daily Job Match Report - {len(matched_jobs)} Jobs Found"
    msg["From"] = config.SENDER_EMAIL
    msg["To"] = config.RECEIVER_EMAIL
    msg.attach(MIMEText(html_content, "html"))

    try:
        print(f"Connecting to SMTP server {config.SMTP_SERVER}:{config.SMTP_PORT}...")
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.starttls()
        server.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)
        print("Logged in successfully. Sending email...")
        server.sendmail(config.SENDER_EMAIL, config.RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
