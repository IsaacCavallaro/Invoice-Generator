from invoice_generator import generate_invoice_pdf, send_invoice_email, get_next_invoice_number, load_email_addresses, save_email_address
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

    email_addresses = load_email_addresses()
    print("Saved email addresses:")
    for key, value in email_addresses.items():
        print(f"{key}: {value}")

    receiver_email_choice = input("Choose an email address (enter the key) or type a new email: ")

    if receiver_email_choice in email_addresses:
        receiver_email = email_addresses[receiver_email_choice]
    else:
        receiver_email = receiver_email_choice
        save_email_choice = input("Do you want to save this email address? (yes/no): ")
        if save_email_choice.lower() == "yes":
            name = input("Enter a name for this email address: ")
            save_email_address(name, receiver_email)

    invoice_number = get_next_invoice_number()

    invoice_data = {
        'billed_to': billed_to,
        'amount': amount,
        'item_details': item_details,
        'invoice_from': invoice_from,
        'invoice_number': invoice_number
    }

    generate_invoice_pdf(invoice_data, template_file, output_file)
    send_invoice_email(sender_email, sender_password, receiver_email, output_file)

if __name__ == "__main__":
    main()
