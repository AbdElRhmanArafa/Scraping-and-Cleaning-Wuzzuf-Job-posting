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

## Run script in Linux
### Prerequisites

To follow this guide, you must have sudo privileged account access to the Ubuntu system. Additionally, some examples may require a desktop environment to be installed.

#### Step 1: Installing Google Chrome

To install the latest Google Chrome browser on Ubuntu and Debian systems, follow these steps:

1. Download the latest Google Chrome Debian package on your system:
   ```
   wget -nc https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb 
   ```

2. Install Google Chrome from the locally downloaded file using the following commands:
   ```
   sudo apt update 
   sudo apt install -f ./google-chrome-stable_current_amd64.deb 
   ```

   Press 'y' for all the confirmations asked by the installer. This will complete the installation of Google Chrome on your Ubuntu or Debian system and also create an Apt PPA file for further upgrades.

#### Step 2: Installing Selenium and Webdriver for Python

To run Python scripts, we will use a virtual environment. Follow these steps to create the virtual environment and install the required Python modules:

1. Create a directory to store Python scripts and switch to the newly created directory:
   ```
   mkdir tests && cd tests 
   ```

2. Set up the Python virtual environment and activate it:
   ```
   python3 -m venv venv 
   source venv/bin/activate 
   ```

   Once the environment is activated, you will find the updated prompt.

3. Use PIP to install the `selenium` and `webdriver-manager` Python modules under the virtual environment:
   ```
   pip install selenium webdriver-manager
   ```
