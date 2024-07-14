from invoice_generator import generate_invoice_pdf, send_invoice_email, get_next_invoice_number, load_email_addresses, save_email_address, choose_or_enter_email
import os
from dotenv import load_dotenv

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

    receiver_email = choose_or_enter_email() 

    invoice_number = get_next_invoice_number()

    invoice_data = {
        'billed_to': billed_to,
        'amount': amount,
        'item_details': item_details,
        'invoice_from': invoice_from,
        'invoice_number': invoice_number
    }

    generate_invoice_pdf(invoice_data, template_file, output_file)
    send_invoice_email(sender_email, sender_password, receiver_email, output_file, invoice_number)

if __name__ == "__main__":
    main()
