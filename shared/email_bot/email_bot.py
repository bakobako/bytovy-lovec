import resend


def generate_email_html(links, user_name="Valued Customer"):
  html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>New Real Estate Listings</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            h1 {{
                color: #2c3e50;
            }}
            ul {{
                padding-left: 20px;
            }}
            li {{
                margin-bottom: 10px;
            }}
            a {{
                color: #3498db;
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            .footer {{
                margin-top: 20px;
                font-size: 12px;
                color: #7f8c8d;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>New Real Estate Listings</h1>
            <p>Hello {user_name},</p>
            <p>We've found some new real estate listings that match your preferences:</p>
            <ul>
    """

  for i, link in enumerate(links, 1):
    html += f"<li><a href='{link}'>Listing #{i}</a></li>"

  html += f"""
            </ul>
            <p>Click on the links above to view the details of each listing.</p>
            <p>Happy house hunting!</p>
            <div class="footer">
                <p>This email was sent based on your preferences. To update your preferences or unsubscribe, please visit our website.</p>
            </div>
        </div>
    </body>
    </html>
    """

  return html


# Example usage:
links = [
  "https://example.com/listing1",
  "https://example.com/listing2",
  "https://example.com/listing3"
]

email_html = generate_email_html(links, "Adam")

resend.api_key = "get_key_from_resend"

params: resend.Emails.SendParams = {
  "from": "Bytovy Lovec <adam@bytovylovec.cz>",
  "to": ["bakoad@gmail.com"],
  "subject": "Found new listings",
  "html": f"{email_html}"
}

email = resend.Emails.send(params)
print(email)

