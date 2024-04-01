import pandas as pd
import re
import spacy
from nltk.corpus import stopwords
import datetime
import requests
from bs4 import BeautifulSoup
import random

# Load English language model
nlp = spacy.load("en_core_web_sm")


# Function to extract time ago from job date
def extract_time_ago(s):
    match = re.search(
        r"(\d+) (day|days|minute|minutes|month|months|year|years|hour|hours) ago",
        s,
    )
    if match:
        value = int(match.group(1))
        unit = match.group(2)
        if unit in ["day", "days"]:
            return pd.Timestamp("now") - pd.DateOffset(days=value)
        elif unit in ["minute", "minutes"]:
            return pd.Timestamp("now") - pd.DateOffset(minutes=value)
        elif unit in ["month", "months"]:
            return pd.Timestamp("now") - pd.DateOffset(months=value)
        elif unit in ["year", "years"]:
            return pd.Timestamp("now") - pd.DateOffset(years=value)
        elif unit in ["hour", "hours"]:
            return pd.Timestamp("now") - pd.DateOffset(hours=value)
    else:
        return None


# Load CSV file
today = datetime.datetime.now().strftime("%Y-%m-%d")
filename = f"{today}.csv"
df = pd.read_csv(filename)

# Drop duplicate rows
df.drop_duplicates(inplace=True)

# Apply function to extract posted datetime
df["posted_datetime"] = df["job_date"].apply(extract_time_ago)

# Extract month and year from posted datetime
df["month"] = df["posted_datetime"].dt.month
df["year"] = df["posted_datetime"].dt.year


# Function to map location to country
def loc_country(x):
    country_mapping = {
        "egypt": "Egypt",
        "lebanon": "Lebanon",
        "libya": "Libya",
        "emirates": "Emirates",
        "saudi arabia": "Saudi Arabia",
        "united states": "United States",
        "uganda": "Uganda",
        "greece": "Greece",
        "kuwait": "Kuwait",
        "latvia": "Latvia",
        "india": "India",
        "netherlands": "Netherlands",
        "jordan": "Jordan",
        "canada": "Canada",
        "qatar": "Qatar",
        "argentina": "Argentina",
    }

    x_lower = x.lower()

    for keyword, country_name in country_mapping.items():
        if keyword in x_lower:
            return country_name

    return "unknown"


# Apply location to country mapping
df["country"] = df["job_location"].apply(loc_country)


# Function to clean and standardize gender
def gender(x):
    if x in ["Male", "Males"]:
        x = "Male"
    elif x in ["Female", "Females"]:
        x = "Female"
    else:
        x = "Both"
    return x


# Apply gender cleaning
df["gender"] = df["gender"].apply(gender)


# Function to extract experience range
def extract_experience_range(experience):
    numbers = re.findall(r"\d+", experience)
    if len(numbers) == 2:
        return (int(numbers[0]), int(numbers[1]))
    elif len(numbers) == 1:
        return int(numbers[0])
    else:
        return -1


# Function to process job data
def process_job(row):
    job_name = row["job_name"]
    experience_needed = row["experience_needed"]

    if "Junior" in job_name:
        row["career_level"] = "Junior"
        row["job_name"] = job_name.replace("Junior", "").strip()
    elif "Senior" in job_name:
        row["career_level"] = "Senior"
        row["job_name"] = job_name.replace("Senior", "").strip()
    else:
        if type(experience_needed) is tuple:
            if experience_needed[0] > 5:
                row["career_level"] = "Senior"
            elif 0 < experience_needed[0] <= 5:
                row["career_level"] = "Mid-Level"
            elif experience_needed[0] == 0:
                row["career_level"] = "Junior"
        elif type(experience_needed) is int:
            if experience_needed == 0:
                row["career_level"] = "Junior"
            elif 0 < experience_needed <= 5:
                row["career_level"] = "Mid-Level"
        career = row["career_level"]
        if (
            "Manager" in career
            or "Senior_Management_(CEO,_GM,_Director,_Head" in career
        ):
            row["career_level"] = "Not_Specified"
    return row


# Remove duplicate data ignoring the "search_key" column
df = df.drop_duplicates(subset=df.columns[:-1])

# Filter for rows where "job_categories" contains "Development"
mask = df["job_categories"].str.contains("Development")
df = df[mask]

# Change "experience_needed"
df["experience_needed"] = df["experience_needed"].apply(
    extract_experience_range
)

# Apply the processing function to each row
df = df.apply(process_job, axis=1)

# Check and update "career_level" and "experience_needed"
mask_not_specified = (df["career_level"] == "Not_Specified") & (
    df["experience_needed"] != -1
)
mask_not_specified_mid_level = (
    (mask_not_specified)
    & (
        0
        < df["experience_needed"].apply(
            lambda x: x[0] if type(x) is tuple else x
        )
    )
    & (
        df["experience_needed"].apply(lambda x: x[1] if type(x) is tuple else x)
        <= 5
    )
)
mask_not_specified_junior = (mask_not_specified) & (
    df["experience_needed"].apply(lambda x: x[0] if type(x) is tuple else x)
    == 0
)
mask_not_specified_senior = (mask_not_specified) & (
    df["experience_needed"].apply(lambda x: x[0] if type(x) is tuple else x) > 5
)

mask_experience_needed = (df["career_level"] != "Not_Specified") & (
    df["experience_needed"] == -1
)
mask_experience_needed_junior = (mask_experience_needed) & (
    df["career_level"] == "Junior"
)
mask_experience_needed_mid_level = (mask_experience_needed) & (
    df["career_level"] == "Mid-Level"
)
mask_experience_needed_senior = (mask_experience_needed) & (
    df["career_level"] == "Senior"
)

df.loc[mask_not_specified_mid_level, "career_level"] = "Mid-Level"
df.loc[mask_not_specified_junior, "career_level"] = "Junior"
df.loc[mask_not_specified_senior, "career_level"] = "Senior"

df.loc[mask_experience_needed_junior, "experience_needed"] = 0
df.loc[mask_experience_needed_mid_level, "experience_needed"] = 3
df.loc[mask_experience_needed_senior, "experience_needed"] = 6

mask_entry_level = df["career_level"].str.contains("Entry_Level_")
df.loc[mask_entry_level, "career_level"] = "Junior"
df.loc[mask_entry_level, "experience_needed"] = 0

mask_student = df["career_level"].str.contains("Student_")
df.loc[mask_student, "career_level"] = "Student"
df.loc[mask_student, "experience_needed"] = 0


# Function to filter job categories
def filter_job_categories(x):
    if "IT/Software Development".lower() in x.lower():
        x = "IT/Software Development"
    else:
        x = "other"
    return x


# Apply job category filtering
df["job_categories"] = df["job_categories"].apply(filter_job_categories)

# Drop rows with job categories 'other'
df = df.drop(df[df["job_categories"] == "other"].index)
df = df.reset_index(drop=True)


# Function to filter career level
def filter_career(x):
    if x in ["Not_Specified", "Junior"]:
        result = "Entry Level"
    else:
        result = x
    return result


# Apply career level filtering
df["career_level"] = df["career_level"].apply(filter_career)


def salary(x):
    salary_mapping = {
        "Senior front end": (25000, 40000),
        "Mid-Level front end": (15000, 25000),
        "Entry Level front end": (8000, 15000),
        "Senior back end": (25000, 40000),
        "Mid-Level back end": (15000, 25000),
        "Entry Level back end": (8000, 15000),
        "Senior full stack": (30000, 45000),
        "Mid-Level full stack": (18000, 30000),
        "Entry Level full stack": (10000, 18000),
        "Entry Level Data Scientist": (15000, 25000),
        "Mid-Level Data Scientist": (25000, 40000),
        "Senior Data Scientist": (40000, 60000),
        "Entry Level DevOps": (10000, 20000),
        "Mid-Level DevOps": (20000, 35000),
        "Senior DevOps": (30000, 50000),
    }
    salary_range = salary_mapping.get(x)
    if salary_range:
        return salary_range
    else:
        random_key = random.choice(list(salary_mapping.keys()))
        salary_range = salary_mapping.get(random_key)
        return salary_range


for index, row in df.iterrows():
    key_job = str(row["key_job"])
    career_level = str(row["career_level"])
    salary_range = salary(career_level + " " + key_job)
    df.at[index, "salary"] = salary_range


# Function to remove punctuations from text
def remove_punctuations(row):
    return re.sub(r"[^\w\s]", " ", row).lower()


# Apply punctuation removal to job description, job requirements, and skills and tools
df["job_description"] = df["job_description"].apply(remove_punctuations)
df["job_requirements"] = df["job_requirements"].apply(remove_punctuations)
df["skills_and_tools"] = df["skills_and_tools"].apply(remove_punctuations)

# Define stop words
stop_words = stopwords.words("english")
bad_words = [
    "computer_science",
    "information_technology_it",
    "software_development",
    "software_engineering",
    "engineering",
    "english",
    "software",
    "years",
    "applications",
    "build",
    "create",
    "development",
    "improve",
    "developers",
    "features",
    "ensure",
    "cairo",
    "information_technology_",
    "web_development",
    "computer_engineering",
    "end",
    "e",
    "g",
    "eg",
]

# Add bad words to stop words list
for word in bad_words:
    stop_words.append(word)


# Function to remove stop words from text
def remove_stop_words(row):
    row = str((row))
    text_combination = row.split(" ")
    non_stop_words = []
    for word in text_combination:
        if word.lower() not in stop_words:
            non_stop_words.append(word)

    return non_stop_words


# Apply stop words removal to job description, job requirements, and skills and tools
df["job_description"] = df["job_description"].apply(remove_stop_words)
df["job_requirements"] = df["job_requirements"].apply(remove_stop_words)
df["skills_and_tools"] = df["skills_and_tools"].apply(remove_stop_words)


# Function to extract relevant information from text using NER
def extract_information(job):
    job = str(job)
    doc = nlp(job)

    # Extract entities or keywords based on your requirements
    relevant_info = set()
    entities_to_extract = [
        "Extra points",
        "Proficient understanding",
        "Understanding",
        "Skill",
        "degree",
        "Responsibilties",
        "Engage",
        "Experience",
        "trong troubleshooting skill",
        "Basic understanding",
    ]
    for ent in doc.ents:
        if ent.label_ in entities_to_extract:
            relevant_info.add(ent.text)

    # If no relevant entities found, return the first few sentences
    if not relevant_info:
        return ". ".join(job.split(".")[:2]).strip()

    # Return the extracted relevant information as a string
    return ", ".join(relevant_info)


# Apply information extraction to job description, job requirements, and skills and tools
df["job_description_info"] = df["job_description"].apply(extract_information)
df["job_requirements_info"] = df["job_requirements"].apply(extract_information)
df["skills_and_tools_info"] = df["skills_and_tools"].apply(extract_information)


# Function to clean and tokenize text
def clean_and_tokenize(text):
    # Convert text to lowercase
    text = str(text)
    text = text.lower()
    # Remove punctuation
    text = re.sub(r"[^\w\s]", "", text)
    return text


# Apply tokenization to job description, job requirements, and skills and tools information
df["job_requirements_info"] = df["job_requirements_info"].apply(
    clean_and_tokenize
)
df["job_description_info"] = df["job_description_info"].apply(
    clean_and_tokenize
)
df["skills_and_tools_info"] = df["skills_and_tools_info"].apply(
    clean_and_tokenize
)

# Drop unnecessary columns
df.drop(
    [
        "job_date",
        "job_requirements",
        "job_description",
        "skills_and_tools",
        "job_categories",
    ],
    axis=1,
    inplace=True,
)


# Function to clean string
def convert_to_str(raw):
    cleaned_str = ""
    for char in raw:
        if char.isalpha() or char.isdigit() or char in ["'", ",", " "]:
            cleaned_str += char
    return cleaned_str.strip(" ,")


# Apply string cleaning to extracted information columns
df["job_description_info"] = df["job_description_info"].apply(convert_to_str)
df["job_requirements_info"] = df["job_requirements_info"].apply(convert_to_str)
df["skills_and_tools_info"] = df["skills_and_tools_info"].apply(convert_to_str)

# To remove any rows containing "Desk" in the job_name
df = df[~df["job_name"].str.contains("Desk")]
df["Social Media Links"] = ""

for index, row in df.iterrows():
    url = row["url_company"]
    if pd.notnull(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        # Extract information from HTML Initialize variables to store extracted information
        industry = None
        company_size = None
        Founded = None
        profile_section = soup.find("div", {"id": "profile-section"})
        if profile_section:
            company_size_tag = profile_section.findAll("span")
            for span in company_size_tag:
                # Find spans with class css-3b60s (indicating label)
                label_span = span.find("span", class_="css-3b60s")
                if label_span:
                    label = label_span.get_text(strip=True)
                    # Extract location
                    # Extract industry
                    if "Industry" in label:
                        industry = span.find(
                            "span", class_="css-16heon9"
                        ).get_text(strip=True)
                    # Extract company size
                    elif "Company Size" in label:
                        company_size = span.find(
                            "span", class_="css-16heon9"
                        ).get_text(strip=True)
                    elif "Founded" in label:
                        Founded = span.find(
                            "span", class_="css-16heon9"
                        ).get_text(strip=True)
        social_media_links = []

        # Extracting links with specific class
        links = soup.find_all("a", class_="css-u8fh7w")
        for link in links:
            social_media_links.append(link["href"])
        website_url = ""

        # Extracting website URL with specific class
        website_link = soup.find("a", class_="css-cttont")
        if website_link:
            website_url = website_link["href"]
            df.at[index, "Website"] = website_url

        # Update DataFrame with extracted information
        df.at[index, "Company Size"] = company_size
        df.at[index, "Founded"] = Founded
        df.at[index, "Specialities"] = industry
        df.at[index, "Social Media Links"] = social_media_links


def extract_data_from_url(url):
    # Prepend 'http://' or 'https://' if scheme is missing
    url = str(url)
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    try:
        html_content = requests.get(url, timeout=20)
        soup = BeautifulSoup(html_content.text, "html.parser")

        # Extract meta tags
        meta_tags = soup.find_all("meta")

        # Extract title tag
        title_tag = soup.find("title")
        title = title_tag.text if title_tag else "No title found"

        # Extract description from meta tags
        description = None
        for tag in meta_tags:
            if tag.get("name", "").lower() == "description":
                description = tag.get("content")
                break

        og_image_tag = soup.find("meta", property="og:image")
        og_image = (
            og_image_tag.get("content") if og_image_tag else "No og:image found"
        )

        return title, description, og_image
    except Exception as e:
        print(f"Error processing URL {url}: {e}")
        return "Error", "Error", "Error"


# get mate-data
for index, row in df.iterrows():
    web_url = row["Website"]
    if pd.notnull(web_url) and web_url != "nan":
        title, description, og_image = extract_data_from_url(web_url)
        # Update DataFrame with extracted information
        df.at[index, "title"] = title
        df.at[index, "description"] = description
        df.at[index, "og_image"] = og_image


# Save the processed dataframe to CSV
df.to_csv(filename)
