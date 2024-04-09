import os
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import smtplib
from email.mime.text import MIMEText
from datetime import date
from PyPDF2 import PdfWriter, PdfReader
from decimal import Decimal
import io
from reportlab.platypus import Table, TableStyle
load_dotenv(".envrc")

def draw_billed_to(can, billed_to_value, start_x, start_y, available_width):
    bold_font = 'Helvetica-Bold'
    normal_font = 'Helvetica'
    can.setFont(bold_font, 10)
    can.drawString(start_x, start_y, "Billed to:")

    # Calculate the position for the value
    value_x = start_x + 70  # Adjust the position for value
    value_y = start_y
    billed_to_value = str(billed_to_value)
    can.setFont(normal_font, 10)
    can.drawString(value_x, value_y, billed_to_value)


def draw_invoice_table(can, item_details, amount, start_x, start_y, available_width, table_height):
    table_width = available_width
    amount_with_prefix = f"${amount}"

    # Draw table for Item and Total
    item_total_data = [
        ["ITEM", "AMOUNT"],
        [item_details, amount_with_prefix]
    ]
    table = Table(item_total_data, colWidths=[table_width / 2] * 2, rowHeights=[table_height / 2] * 2)
    table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, (0, 0, 0)),
                               ('BOX', (0, 0), (-1, -1), 0.25, (0, 0, 0)),
                               ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),  # Bold headings
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center alignment
                               ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))  # Vertical alignment
    table.wrapOn(can, table_width, table_height)
    
    # Calculate the x-coordinate to center the table horizontally
    table_x = start_x + (available_width - table_width) / 2

    # Draw the table on the canvas
    table.drawOn(can, table_x, start_y - table_height)


def draw_payment_details(can, start_x, start_y, available_width):
    bold_font = 'Helvetica-Bold'
    normal_font = 'Helvetica'
    can.setFont(normal_font, 10)

    payment_details = {
        "Payment Method": os.getenv("PAYMENT_METHOD"),
        "Account No": os.getenv("ACCOUNT_NO"),
        "Account Name": os.getenv("ACCOUNT_NAME"),
        "BSB": os.getenv("BSB")
    }

    payment_start_y = start_y - inch  # Adjust as needed

    # Draw each payment detail line by line
    for key, value in payment_details.items():
        # Draw key in bold
        can.setFont(bold_font, 10)
        can.drawString(start_x, payment_start_y, f"{key}: ")

        # Draw value in normal font
        can.setFont(normal_font, 10)
        can.drawString(start_x + 100, payment_start_y, value)

        payment_start_y -= 15  # Adjust the spacing between lines as needed

def draw_invoice_date(can, start_x, start_y):
    bold_font = 'Helvetica-Bold'
    normal_font = 'Helvetica'
    can.setFont(bold_font, 10)

    # Draw "Date:" key
    can.drawString(start_x, start_y, "Date: ")
    value_x = start_x + 70  # Adjust the position for value
    value_y = start_y

    # Get today's date
    today_date = date.today().strftime("%Y-%m-%d")
    can.setFont(normal_font, 10)
    can.drawString(value_x, value_y, today_date)

def draw_invoice_from(can, invoice_from, start_x, start_y):
    bold_font = 'Helvetica-Bold'
    normal_font = 'Helvetica'
    can.setFont(bold_font, 10)
    can.drawString(start_x, start_y, "From:")

    value_x = start_x + 70  # Adjust the position for value
    value_y = start_y
    invoice_from = str(invoice_from)

    can.setFont(normal_font, 10)
    can.drawString(value_x, value_y, invoice_from)


def generate_invoice_pdf(invoice_data, template_file, output_file):
    existing_pdf = PdfReader(template_file)
    page = existing_pdf.pages[0]

    # Create a canvas for the page
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)

    # Calculate the center position of the page
    page_width, page_height = map(float, page.mediabox.upper_right)
    
    # Define left and right margins
    left_margin = inch
    right_margin = inch

    # Calculate the available width for the table
    available_width = page_width - left_margin - right_margin

    # Define the height of the table
    table_height = inch * 1  # Set the height as per your requirement

    # Calculate the starting coordinates for the "Billed to" details
    billed_to_start_y = page_height - inch - 150  # Adjusted to position higher on the page

    # Calculate the starting coordinates for the table
    table_start_y = billed_to_start_y - table_height - 0.25 * inch  # Adjust as needed for reduced spacing between "Billed to" and table

    # Calculate the starting x-coordinate to align both the "Billed to" details and the table with the left margin
    start_x = left_margin

    # Draw invoice date
    draw_invoice_date(can, start_x, billed_to_start_y)

    # Calculate the position for the "Billed to" details
    billed_to_start_y -= 0.25 * inch  # Adjust as needed to reduce the gap

    # Draw Billed to details
    draw_billed_to(can, invoice_data['billed_to'], start_x, billed_to_start_y, available_width)

    # Draw invoice table
    draw_invoice_table(can, invoice_data['item_details'], invoice_data['amount'], start_x, table_start_y, available_width, table_height)

    # Calculate the starting coordinates for the payment details
    payment_start_y = table_start_y - inch * 0.5  # Adjust as needed to reduce the gap

    # Draw payment details
    draw_payment_details(can, start_x, payment_start_y, available_width)
    
    # Calculate the position for the "From" details
    from_start_y = billed_to_start_y - 0.25 * inch  # Adjust position as needed for reduced gap

    # Draw "From" details
    draw_invoice_from(can, invoice_data['invoice_from'], start_x, from_start_y)

    # Save the canvas
    can.save()

    # Move to the beginning of the StringIO buffer
    packet.seek(0)
    new_pdf = PdfReader(packet)
    overlay = new_pdf.pages[0]

    # Merge the overlay with the existing page content
    page.merge_page(overlay)

    # Write the output PDF to a file
    output = PdfWriter()
    output.add_page(page)
    with open(output_file, "wb") as output_stream:
        output.write(output_stream)

def send_invoice_email(sender_email, sender_password, receiver_email, pdf_file):
    # Email settings
    subject = "Invoice"
    body = "Please find attached invoice."

    # Create message container
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Attach invoice PDF
    with open(pdf_file, 'rb') as attachment:
        part = MIMEBase('application', 'pdf')
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(pdf_file)}')
    msg.attach(part)

    # Attach body
    msg.attach(MIMEText(body, 'plain'))

    # Connect to SMTP server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, sender_password)

    # Send email
    text = msg.as_string()
    server.sendmail(sender_email, receiver_email, text)
    server.quit()

def main():
    load_dotenv(".envrc")
    billed_to = input("Enter billed to details: ")
    amount = float(input("Enter invoice amount: "))
    item_details = input("Enter item details: ")
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    template_file = "invoice_template.pdf"
    output_file = os.path.join(desktop_path, "invoice.pdf")
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    invoice_from = os.getenv("INVOICE_FROM")
    receiver_email = input("Enter email to send invoice to: ")

    invoice_data = {
        'billed_to': billed_to,
        'amount': amount,
        'item_details': item_details,
        'invoice_from': invoice_from  
    }

    generate_invoice_pdf(invoice_data, template_file, output_file)
    send_invoice_email(sender_email, sender_password, receiver_email, output_file)

if __name__ == "__main__":
    main()
