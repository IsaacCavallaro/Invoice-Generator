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

def get_next_invoice_number():
    try:
        with open("last_invoice_number.txt", "r") as file:
            content = file.read().strip()
            if not content:
                raise ValueError("The file is empty.")
            last_invoice_number = int(content)
    except (FileNotFoundError, ValueError) as e:
        raise RuntimeError("Error reading the last invoice number: " + str(e))

    next_invoice_number = last_invoice_number + 1

    with open("last_invoice_number.txt", "w") as file:
        file.write(str(next_invoice_number))

    return next_invoice_number


def draw_invoice_number(can, invoice_number, start_x, start_y):
    bold_font = 'Helvetica-Bold'
    normal_font = 'Helvetica'
    can.setFont(bold_font, 10)
    can.drawString(start_x, start_y, "Invoice No: ")

    value_x = start_x + 100
    value_y = start_y

    can.setFont(normal_font, 10)
    can.drawString(value_x, value_y, str(invoice_number))

def draw_billed_to(can, billed_to_value, start_x, start_y, available_width):
    bold_font = 'Helvetica-Bold'
    normal_font = 'Helvetica'
    can.setFont(bold_font, 10)
    can.drawString(start_x, start_y, "Billed to:")

    value_x = start_x + 70
    value_y = start_y
    billed_to_value = str(billed_to_value)
    can.setFont(normal_font, 10)
    can.drawString(value_x, value_y, billed_to_value)

def draw_invoice_table(can, item_details, amount, start_x, start_y, available_width, table_height):
    table_width = available_width
    amount_with_prefix = f"${amount}"

    item_total_data = [
        ["ITEM", "AMOUNT"],
        [item_details, amount_with_prefix]
    ]
    table = Table(item_total_data, colWidths=[table_width / 2] * 2, rowHeights=[table_height / 2] * 2)
    table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, (0, 0, 0)),
                               ('BOX', (0, 0), (-1, -1), 0.25, (0, 0, 0)),
                               ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
    table.wrapOn(can, table_width, table_height)

    table_x = start_x + (available_width - table_width) / 2

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

    payment_start_y = start_y - inch

    for key, value in payment_details.items():
        can.setFont(bold_font, 10)
        can.drawString(start_x, payment_start_y, f"{key}: ")

        can.setFont(normal_font, 10)
        can.drawString(start_x + 100, payment_start_y, value)

        payment_start_y -= 15

def draw_invoice_date(can, start_x, start_y):
    bold_font = 'Helvetica-Bold'
    normal_font = 'Helvetica'
    can.setFont(bold_font, 10)

    can.drawString(start_x, start_y, "Date: ")
    value_x = start_x + 70
    value_y = start_y

    today_date = date.today().strftime("%Y-%m-%d")
    can.setFont(normal_font, 10)
    can.drawString(value_x, value_y, today_date)

def draw_invoice_from(can, invoice_from, start_x, start_y):
    bold_font = 'Helvetica-Bold'
    normal_font = 'Helvetica'
    can.setFont(bold_font, 10)
    can.drawString(start_x, start_y, "From:")

    value_x = start_x + 70
    value_y = start_y
    invoice_from = str(invoice_from)

    can.setFont(normal_font, 10)
    can.drawString(value_x, value_y, invoice_from)

def generate_invoice_pdf(invoice_data, template_file, output_file):
    existing_pdf = PdfReader(template_file)
    page = existing_pdf.pages[0]

    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)

    page_width, page_height = map(float, page.mediabox.upper_right)
    left_margin = inch
    right_margin = inch
    available_width = page_width - left_margin - right_margin
    table_height = inch * 1

    billed_to_start_y = page_height - inch - 150
    table_start_y = billed_to_start_y - table_height - 0.25 * inch
    start_x = left_margin

    draw_invoice_date(can, start_x, billed_to_start_y)

    billed_to_start_y -= 0.25 * inch

    draw_billed_to(can, invoice_data['billed_to'], start_x, billed_to_start_y, available_width)

    draw_invoice_table(can, invoice_data['item_details'], invoice_data['amount'], start_x, table_start_y, available_width, table_height)

    payment_start_y = table_start_y - inch * 0.5

    draw_payment_details(can, start_x, payment_start_y, available_width)
    
    from_start_y = billed_to_start_y - 0.25 * inch

    draw_invoice_from(can, invoice_data['invoice_from'], start_x, from_start_y)

    invoice_number = invoice_data['invoice_number']
    invoice_number_start_y = from_start_y - 0.25 * inch
    draw_invoice_number(can, invoice_number, start_x, invoice_number_start_y)

    can.save()

    packet.seek(0)
    new_pdf = PdfReader(packet)
    overlay = new_pdf.pages[0]

    page.merge_page(overlay)

    output = PdfWriter()
    output.add_page(page)
    with open(output_file, "wb") as output_stream:
        output.write(output_stream)

def send_invoice_email(sender_email, sender_password, receiver_email, pdf_file):
    subject = "Invoice"
    body = "Please find attached invoice."

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    with open(pdf_file, 'rb') as attachment:
        part = MIMEBase('application', 'pdf')
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(pdf_file)}')
    msg.attach(part)

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, sender_password)

    text = msg.as_string()
    server.sendmail(sender_email, receiver_email, text)
    server.quit()
