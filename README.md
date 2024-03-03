# Wuzzuf Data Cleaning and MongoDB Integration

## Description
This project involves cleaning job data scraped from the Wuzzuf website and integrating it into a MongoDB database.

## Getting Started
### Prerequisites
- Python 3
- Selenium
- BeautifulSoup
- Pandas
- Spacy
- NLTK

### Installation
1. Clone the repository.
2. Install dependencies using pip:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Run the cleaning script to preprocess the scraped data and save it as a CSV file.
2. Run the saving script to integrate the cleaned data into a MongoDB database.

## Cleaning Process
- The cleaning script applies various data cleaning and preprocessing techniques, including duplicate removal, text extraction, and stop word removal.
- External libraries such as Spacy and NLTK are used for text processing tasks.

## Saving
- The saving script connects to a MongoDB database and inserts the cleaned data into appropriate collections.
- Data is structured in a format suitable for MongoDB storage.

## MongoDB
- MongoDB is used to store the cleaned job data.
- The database consists of collections for companies, locations, skills, and jobs, with appropriate references between them.