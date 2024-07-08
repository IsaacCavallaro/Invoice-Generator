# Invoice Generator

The Invoice Generator is a Python script that automates the creation of professional-looking invoices in PDF format and their transmission via email. It leverages the ReportLab library for PDF generation and the smtplib library for email transmission. Designed as a cost-effective solution, it provides a free alternative to expensive invoice applications, offering essential features without unnecessary costs.

## Features

- Generate customised invoices with:
  - item details
  - invoice number
  - amount
  - billed-to information
  - payment details
- Automatically populate the invoice date with the current date.
- Save commonly used emails for effeciency
- Attach the generated PDF invoice to an email and send it to the recipient.
- Support for environment variables to securely store payment details.

## Run the script

```bash
python3 main.py 
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

### 4. Create initial emails

- Create a file called `email_addresses.json` and add your common emails with a short name which will map to the email address:

```json
{
    "test-name": "test-email@test.com",
    "test-again": "test-again@test.com"
}
```

### Additional Tips

- Ensure Python 3.x is installed on your system. To check your Python version, run:

```bash
python3 --version
```

- Make sure the version displayed is compatible with the dependencies specified in requirements.txt.

- Customise `invoice_template.pdf` for your specific invoice layout if needed.
