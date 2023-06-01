# Web Scraper for JW.ORG in German language and Saving Data to Firebase Firestore

This is a Python web scraper that allows you to scrape all bible books available on the German version of the JW.ORG website (wol.jw.org) and save the scraped data to a Firebase Firestore database.

## Requirements

To run this scraper, you will need:

- Python 3.6+
- requests library
    - beautifulsoup4 library
    - firebase-admin library
- A Firebase project with Firestore enabled

## Installation

1. Clone the repository to your local machine.
```bash
git clone https://github.com/mildnl/python-docx-script.git
```
2. Install the required libraries using pip.
```bash
pip install requests beautifulsoup4 firebase-admin
```
3. Download the service account key file from your Firebase project and place it in the root directory of the repository.
4. Update the config.py file with your Firebase project details and the collection name you want to use.
```python
# Firebase configuration
FIREBASE_CONFIG = {
    "apiKey": "YOUR_API_KEY",
    "authDomain": "YOUR_AUTH_DOMAIN",
    "projectId": "YOUR_PROJECT_ID",
    "storageBucket": "YOUR_STORAGE_BUCKET",
    "messagingSenderId": "YOUR_MESSAGING_SENDER_ID",
    "appId": "YOUR_APP_ID"
}

# Firestore configuration
FIRESTORE_COLLECTION_NAME = "YOUR_COLLECTION_NAME"
```
## Usage

To use the scraper, run the following command:

```bash
python scrape.py
```
The scraper will then scrape all the bible books available on the German version of the JW.ORG website and save them to the Firestore database specified in the config/serviceAccountKey.json file.

##Output

The scraper will save the scraped data to the specified Firestore collection in the following format:

```json
{
    Book: "1 Buch Mose (Genisis)"
    Chapter: {
        Number: 1
        Verses: [...]
    }
    ...
    Number: 1
}
```
##Contributing

If you would like to contribute to this repository, please fork the repository and submit a pull request.