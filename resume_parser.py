# importing the required libraries
# pathlib is used to get the filename without the extension
# re is used for regular expressions that will help to extract the contact number and email from the resume
# fuzzywuzzy is used to find the similar strings in the document
# pdfminer is used to extract the text from the pdf
# spacy is used for natural language processing that will help to extract the candidate's name from the resume
from pathlib import Path
import re
from fuzzywuzzy import process
from pdfminer.high_level import extract_text
import spacy
from spacy.matcher import Matcher
 
 
# define a function to get the filename without the extension
def get_filename_without_extension(file_path):
 
    # Convert the file path to a Path object and get the filename without the extension
    filename_without_extension = Path(file_path).stem
    return filename_without_extension
 
 
def clean_filename(text):
    text = text.replace('CV','').replace('cv','')
    # Replace dashes and underscores with spaces
    text = text.replace("-", " ").replace("_", " ")
 
    # Remove parentheses and square brackets
    text = re.sub(r"[()\[\]]", "", text)
 
    # Remove numbers
    text = re.sub(r"\d", "", text)
 
    # Optionally, trim multiple spaces to a single space
    text = re.sub(r"\s+", " ", text).strip()
 
    return text
 


 
# Define a function to find similar strings in a document
# The function will return the top N matches based on the similarity score
# and a similarity threshold
# The function will use the fuzzywuzzy library to find similar strings
# in the document text
# The function will return a list of tuples containing the matched string
# and the similarity score
# The function will also clean the filename by removing dashes, underscores,
# parentheses, square brackets, numbers, and extra spaces

def find_similar_strings_in_document(document_text, filename, top_n=5, similarity_threshold=80):
    filename = clean_filename(filename)
    # Split the document text into words
    words = set(re.findall(r'\b\w+\b', document_text))
 
    # Find the top N matches for the filename from the words in the document
    best_matches = process.extract(filename, list(words), limit=top_n)
 
    # Filter matches based on a similarity threshold
    filtered_matches = [
        match for match in best_matches if match[1] >= similarity_threshold
    ]
    print('filtered matches : ')
    print(filtered_matches)
    return filtered_matches
 
 
# Define a function to extract text from a PDF file 
def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)
 
# Define a function to extract the contact number from the resume
# The function will use regular expressions to find the contact number in the text

def extract_contact_number_from_resume(text):
    contact_number = None
 
   
    pattern1 = r"(\+?(?:212\s*|0)\s*(?:(?:[.-]?\d{3}[.-]?\s*)|(?:\(\d{3}\)\s*)|(?:\d{3}\s*))?(?:[.-]?\d{3}[.-]?\s*){2}\d{3})"
    match1 = re.search(pattern1, text)
    if match1:
        contact_number = match1.group()
    else:
        # If not found, try to find numbers in the format 06 34 34 85 50
        pattern2 = r"(?:\b\d{2}\s*\d{2}\s*\d{2}\s*\d{2}\s*\d{2}\b)"
        match2 = re.search(pattern2, text)
        if match2:
            contact_number = match2.group()
 
    return contact_number
 

# Define a function to extract the email address from the resume
# The function will use regular expressions to find the email address in the text 
def extract_email_from_resume(text):
    email = None
 
    # Use regex pattern to find a potential email address
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    match = re.search(pattern, text)
    if match:
        email = match.group()
 
    return email

# Define a function to extract skills from the resume
# The function will use a list of skills and a regular expression pattern 
def extract_skills_from_resume(text, skills_list):
    skills = []
 
    for skill in skills_list:
        pattern = r"\b{}\b".format(re.escape(skill))
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            skills.append(skill)
 
    return skills
 

# Define a function to extract education information from the resume
# The function will use a regular expression pattern to find education information
def extract_education_from_resume(text):
    education = []
 
    # Use regex pattern to find education information
    pattern = r"(?i)(faculté|école|université|institut|grande école|bachelor|master|doctorat|ensa|fst|ensam|ehtp|uir|internationale|école|rabat)\b\s*(.*?)(?=\.|\n|;|,|$)"
    matches = re.findall(pattern, text)
    for match in matches:
        education.append(match[0] + " " + match[1].strip())
 
    return education
 
 

# Define a function to extract the candidate's name from the resume
# The function will use spaCy for natural language processing
# and a pattern matcher to find the name in the text
def extract_name(resume_text):
    # Load the spaCy model
    nlp = spacy.load('fr_core_news_sm')
    # Initialize the matcher
    matcher = Matcher(nlp.vocab)
 
    # Define name patterns
    patterns = [
        [{'IS_ALPHA': True, 'OP': '+'}, {'IS_ALPHA': True, 'OP': '+'}],  # First name and Last name 
        [{'IS_ALPHA': True, 'OP': '+'}, {'IS_ALPHA': True, 'OP': '+'}, {'IS_ALPHA': True, 'OP': '+'}],  # First name, Middle name, and Last name
        [{'IS_ALPHA': True, 'OP': '+'}, {'IS_ALPHA': True, 'OP': '+'}, {'IS_ALPHA': True, 'OP': '+'}, {'IS_ALPHA': True, 'OP': '+'}]  # First name, Middle name, Middle name, and Last name
    ]
 
    for pattern in patterns:
        matcher.add('NAME', patterns=[pattern])
 
    doc = nlp(resume_text)
    matches = matcher(doc)
 
    for match_id, start, end in matches:
        span = doc[start:end]
        return span.text
 
    return None
 
# Define a function to count the total months of experience from the resume
# The function will use regular expressions to find date ranges in the experience section
# and calculate the total months worked 
def count_experience_months(resume_text):
    # Define a pattern to match variations of the experience section title
    experience_pattern = re.compile(r'(?:EXPÉRIENCES PROFESSIONNELLES?|EXPÉRIENCE PROFESSIONNELLE|Professional Experiences & Projects|Exp[ée]riences\s+Professionnelles?|Exp[ée]rienc\s+es\s+pr\s+ofessionnelles?|EXPÉRIENCES?:)', re.IGNORECASE)
 
    # Initialize a flag to track if we are within the experience section
    within_experiences_section = False
    # Initialize variables to store total months worked
    total_months_worked = 0
 
    # French month names mapping
    french_months = {
        'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4,
        'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8,
        'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
    }
 
    # Split the resume text by lines
    lines = resume_text.split('\n')
 
    # Iterate through each line
    for line in lines:
        # Check if the line matches the experience section pattern
        if re.search(experience_pattern, line):
            within_experiences_section = True
            continue  # Skip to the next line
 
        # Check if we are within the experience section
        if within_experiences_section:

            #manage all cases of date ranges in the experience section
           
            # 1. Check if the line contains date ranges in the format "De février 2024 à juillet 2024"
            matches1 = re.findall(r'(?:De|du) (\w+) (\d{4}) (?:à|au) (\w+) (\d{4})', line)
            if matches1:
                for start_month, start_year, end_month, end_year in matches1:
 
                    start_month_num = french_months.get(start_month.lower())
                    end_month_num = french_months.get(end_month.lower())
                    total_months_worked += (int(end_year) - int(start_year)) * 12 + (end_month_num - start_month_num) + 1
 
            # 2. Check if the line contains date ranges in the format "04-2023 - 07-2023"
            matches2 = re.findall(r'(\d{2})-(\d{4}) - (\d{2})-(\d{4})', line)
            if matches2 and not matches1:
                for start_month, start_year, end_month, end_year in matches2:
                    total_months_worked += (int(end_year) - int(start_year)) * 12 + (int(end_month) - int(start_month)) + 1
 
            # 3. Check if  the line contains date ranges in the format "04/2023 - 07/2023" or "2/2024-7/2024"
            matches3 = re.findall(r'(\d{1,2})[/-](\d{4})\s*-\s*(\d{1,2})[/-](\d{4})', line)
            if matches3 and not matches2:
                for start_month, start_year, end_month, end_year in matches3:
                    total_months_worked += (int(end_year) - int(start_year)) * 12 + (int(end_month) - int(start_month)) + 1
 
            # 4. Check if the line contains date ranges in the format "10 Juillet 2023 - 30 août 2023"
            matches4 = re.findall(r'(\d{1,2}) (\w+) (\d{4}) - (\d{1,2}) (\w+) (\d{4})', line)
            if matches4 and not matches3:
                for start_day, start_month, start_year, end_day, end_month, end_year in matches4:
                    start_month_num = french_months.get(start_month.lower())
                    end_month_num = french_months.get(end_month.lower())
                    total_months_worked += (int(end_year) - int(start_year)) * 12 + (end_month_num - start_month_num) + 1
 
    print(total_months_worked)
    # Convert total months worked into years and months
    total_years = total_months_worked / 12
    remaining_months = int(total_months_worked % 12)
 
    return total_years;


# Define a function to extract the LinkedIn profile URL from the resume
# The function will use a regular expression pattern to find LinkedIn profile URLs
def extract_linkedin(resume_text):
    # Define a regular expression pattern to match LinkedIn profile URLs
        linkedin_pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/(?:\w+/)?(?:in|pub|profile)/[\w-]+/?'
          # Find all LinkedIn profile URLs in the resume text
        linkedin_urls = re.findall(linkedin_pattern, resume_text)
        return linkedin_urls;

# this is the main function that will extract all the information from the resume and 
#call all the functions defined above 
def extract_all_data(path):
    resume_paths = [path]
 
    for resume_path in resume_paths:
        text = extract_text_from_pdf(resume_path)
        filename = get_filename_without_extension(resume_path)
        similar_strings = find_similar_strings_in_document(text,filename)
        print(similar_strings)
 
        print("Resume:", resume_path)
        response = dict()
 
 
        name = extract_name(text)
        response['name'] = name
        if name:
            print("Name:", name)
        else:
            print("Name not found")
 
        contact_number = extract_contact_number_from_resume(text)
        if contact_number:
            response['contact_number'] = contact_number
            print("Contact Number:", contact_number.replace('\n',''))
        else:
            print("Contact Number not found")
 
        email = extract_email_from_resume(text)
        if email:
            response['email'] = email
            print("Email:", email)
        else:
            print("Email not found")
 
        skills_list = ['Python', 'Data Analysis', 'Machine Learning', 'Communication', 'Project Management', 'Deep Learning', 'SQL', 'Tableau', 'LWC','Keycloak','Laravel','HTML','CSS','JS','Java','JavaScript']
        extracted_skills = extract_skills_from_resume(text, skills_list)
        if extracted_skills:
            response['extracted_skills'] = extracted_skills
            print("Skills:", extracted_skills)
        else:
            print("No skills found")
 
        extracted_education = extract_education_from_resume(text)
        if extracted_education:
            response['education'] = extracted_education
            print("Education:", extracted_education)
        else:
            print("No education information found")

        exp_mths = count_experience_months(text)
        if exp_mths:
            response['yrs_exp'] = exp_mths
        else:
            print("No Years experience found")
        
        lkdn = extract_linkedin(text)
        if lkdn:
            response['linkedin'] = lkdn
        else:
            print("No Years experience found")
        
        
        return response
