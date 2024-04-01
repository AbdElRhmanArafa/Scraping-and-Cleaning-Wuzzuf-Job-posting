from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup
import numpy as np
import csv
import time as t
import datetime


driver = webdriver.Chrome()

today = datetime.datetime.now().strftime("%Y-%m-%d")
filename = f"{today}.csv"
with open(filename, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(
        [
            "job_name",
            "job_type",
            "company_name",
            "job_location",
            "job_date",
            "num_of_people",
            "experience_needed",
            "career_level",
            "education_level",
            "gender",
            "salary",
            "job_categories",
            "skills_and_tools",
            "job_description",
            "job_requirements",
            "key_job",
            "url_company",
        ]
    )

    jobs = ["front end", "back end", "full stack", "DevOps", "Data Scientist"]
    substring = ["front", "back", "full", "devops", "scien"]
    for job, substr in zip(jobs, substring):
        page = 0
        running = True
        while running:
            response = requests.get(
                f"https://wuzzuf.net/search/jobs?a=spbg&filters%5Bpost_date%5D%5B0%5D=within_1_week&filters%5Broles%5D%5B0%5D=IT%2FSoftware%20Development&q={job}&start={page}"
            )
            soup = BeautifulSoup(response.text, "html.parser")
            link = soup.find_all("h2", attrs={"class": "css-m604qf"})
            div = soup.find_all("div", attrs={"class": "css-d7j1kk"})

            if len(link) <= 0:
                running = False
                break

            for i, d in zip(link, div):
                try:
                    link_url1 = i.find("a", attrs={"class": "css-o171kl"})
                except:
                    break
                link_url2 = link_url1.attrs["href"]
                print(link_url2)

                driver.get(link_url2)

                job_name = driver.find_element(
                    By.CLASS_NAME, "css-f9uh36"
                ).text.strip()

                if substr.lower() in job_name.lower():
                    key_job = job
                else:
                    continue
                job_type = (
                    driver.find_element(By.CLASS_NAME, "css-11rcwxl")
                    .text.replace(" ", "_")
                    .split()
                )

                company_name = (
                    d.find("a", attrs={"class": "css-17s97q8"})
                    .get_text()
                    .replace("-", "")
                    .strip()
                )
                url_company = d.find("a", attrs={"class": "css-17s97q8"})[
                    "href"
                ]

                job_location = (
                    d.find("span", attrs={"class": "css-5wys0k"})
                    .get_text()
                    .replace(",", "")
                    .strip()
                )

                job_date = driver.find_element(
                    By.CLASS_NAME, "css-182mrdn"
                ).text

                try:
                    num_of_people = driver.find_element(
                        By.CLASS_NAME, "css-u1gwks"
                    ).text
                except:
                    num_of_people = "0"

                experience_needed = (
                    driver.find_element(By.CLASS_NAME, "css-3kx5e2")
                    .text.replace(" ", "_")
                    .split()[2]
                )

                career_level = (
                    driver.find_element(By.CLASS_NAME, "css-3kx5e2")
                    .text.replace(" ", "_")
                    .split()[4]
                )

                education_level = (
                    driver.find_element(By.CLASS_NAME, "css-3kx5e2")
                    .text.replace(" ", "_")
                    .split()[6]
                )

                if (
                    driver.find_elements(By.CLASS_NAME, "css-rcl8e5")[
                        3
                    ].text.split()[0]
                    == "Salary:"
                ):
                    gender = "male and female"
                    salary = driver.find_elements(By.CLASS_NAME, "css-rcl8e5")[
                        3
                    ].text.split()[1]
                else:
                    gender = driver.find_elements(By.CLASS_NAME, "css-rcl8e5")[
                        3
                    ].text.split()[1]
                    salary = driver.find_elements(By.CLASS_NAME, "css-rcl8e5")[
                        4
                    ].text.split()[1]

                job_categories = driver.find_element(
                    By.CLASS_NAME, "css-13sf2ik"
                ).text.split("\n")[1:]

                skills_and_tools = (
                    driver.find_element(By.CLASS_NAME, "css-s2o0yh")
                    .text.replace(" ", "_")
                    .split()[1:]
                )

                try:
                    job_description = []
                    y = (
                        driver.find_element(By.CLASS_NAME, "css-1uobp1k")
                        .text.replace(" ", "_")
                        .split()
                    )
                    for i in y:
                        ro = i.replace("_", " ").strip()
                        if ro == "":
                            continue
                        else:
                            job_description.append(ro)
                except:
                    job_description = "none"

                try:
                    job_requirements = []
                    y1 = (
                        driver.find_element(By.CLASS_NAME, "css-1t5f0fr")
                        .text.replace(" ", "_")
                        .split()
                    )
                    for i in y1:
                        ro1 = i.replace("_", " ").strip()
                        if ro1 == "":
                            continue
                        else:
                            job_requirements.append(ro1)
                except:
                    job_requirements = "none"

                row = [
                    job_name,
                    job_type,
                    company_name,
                    job_location,
                    job_date,
                    num_of_people,
                    experience_needed,
                    career_level,
                    education_level,
                    gender,
                    salary,
                    job_categories,
                    skills_and_tools,
                    job_description,
                    job_requirements,
                    key_job,
                    url_company,
                ]
                writer.writerow(row)
                print(row)
            page += 1
driver.quit()
