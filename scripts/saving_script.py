import pandas as pd
from pymongo import MongoClient
import datetime

import similar

# Connect to MongoDB
client = MongoClient(
    "mongodb+srv://abdelrhmanarafa:SzbZ07ndtx0wlIg7@deployment.44r3nxg.mongodb.net/"
)
db = client["JobPostings"]

# Define collection names
company_collection = db["Companies"]
location_collection = db["Locations"]
skill_collection = db["Skills"]
job_collection = db["Jobs"]

today = datetime.datetime.now().strftime("%Y-%m-%d")
filename = f"{today}.csv"

data = pd.read_csv("2024-04-01.csv")

# Iterate over each row
for index, row in data.iterrows():
    # Check if company exists, if not, insert into company_collection
    company_query = {"company_name": row["company_name"]}
    new_company_data = {
        "company_name": row["company_name"],
        "Social Media Links": row["Social Media Links"],
        "Website": row["Website"],
        "Company Size": row["Company Size"],
        "Founded": row["Founded"],
        "Specialities": row["Specialities"],
        "title": row["title"],
        "description": row["description"],
        "og_image": row["og_image"],
    }
    company = company_collection.find_one(company_query)
    if not company:
        # Insert company if it doesn't exist
        company_id = company_collection.insert_one(new_company_data).inserted_id
    else:
        # Update existing company document
        company_collection.update_one(company_query, {"$set": new_company_data})
        company_id = company["_id"]

    # Check if location exists, if not, insert into location_collection
    location = location_collection.find_one(
        {"job_location": row["job_location"]}
    )
    if not location:
        # Insert location if it doesn't exist
        location_id = location_collection.insert_one(
            {"job_location": row["job_location"]}
        ).inserted_id
    else:
        location_id = location["_id"]

    # Split skills and insert each unique skill into skill_collection
    skills = set(row["skills_and_tools_info"].split(" "))
    cleaned_skills = similar.clean_skills(skills, similar.similar_skills)
    skill_ids = []
    for skill in cleaned_skills:
        existing_skill = skill_collection.find_one({"skill_name": skill})
        if not existing_skill:
            # Insert skill if it doesn't exist
            skill_id = skill_collection.insert_one(
                {"skill_name": skill}
            ).inserted_id
        else:
            skill_id = existing_skill["_id"]
        skill_ids.append(skill_id)

    # Insert job data into job_collection, referencing company, location, and skills
    job_data = {
        "job_name": row["job_name"],
        "job_type": row["job_type"],
        "company_id": company_id,
        "location_id": location_id,
        "applyed_people": row["num_of_people"],
        "experience": row["experience_needed"],
        "career_level": row["career_level"],
        "education_level": row["education_level"],
        "gender": row["gender"],
        "salary_range": row["salary"],
        "key_job": row["key_job"],
        "posted_datetime": row["posted_datetime"],
        "month": row["month"],
        "year": row["year"],
        "country": row["country"],
        "job_description": row["job_description_info"],
        "job_requirements": row["job_requirements_info"],
        "skill_ids": skill_ids,
    }
    job_collection.insert_one(job_data)

# Close MongoDB connection
client.close()
