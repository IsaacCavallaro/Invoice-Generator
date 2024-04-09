# Invoice Generator

The Invoice Generator is a Python script that allows users to generate professional-looking invoices in PDF format and send them via email. It utilizes the ReportLab library for PDF generation and the smtplib library for email sending.

## Features

- Generate customized invoices with item details, amount, billed-to information, and payment details.
- Automatically populate the invoice date with the current date.
- Attach the generated PDF invoice to an email and send it to the recipient.
- Support for environment variables to securely store payment details.

## Run the script

```bash
python3 invoice_generator.py  
```

---

## Installation Instructions

### 1. Clone the Repository

```bash
git clone git@github.com:IsaacCavallaro/Invoice-Generator.git
cd invoice-generator
```

---

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Set Up Environment Variables

- If you haven't already installed direnv, you can do so using Homebrew (for macOS users):

```bash
brew install direnv
```

- Create a file called `.envrc` and add the following:

```bash
export PAYMENT_METHOD='Bank Transfer'
export ACCOUNT_NO='YourAccountNumber'
export ACCOUNT_NAME='YourAccountName'
export BSB='YourBSB'
export SENDER_EMAIL='YourEmailAddress'
export SENDER_PASSWORD='YourEmailPassword'
export INVOICE_FROM='YourName'
```

---

- Allow the .envrc file to be loaded:

```bash
direnv allow
```

- Note: Ensure to keep your .envrc file secure and do not share it publicly.

---
