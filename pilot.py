import json
from selenium import webdriver
from chromedriver_py import binary_path
from urllib.parse import urlparse, parse_qs
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from dotenv import load_dotenv
import os
import requests
import re

import time
from docx import Document

from openai import OpenAI, RateLimitError

load_dotenv()

ASU_USERNAME = os.getenv("ASU_USERNAME")
ASU_PASSWORD = os.getenv("ASU_PASSWORD")
SIGN_IN_TIMEOUT = os.getenv("SIGN_IN_TIMEOUT")
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# dont worry i wont steal your data

YOLO_MODE = os.getenv("YOLO_MODE")

YOUR_NAME = os.getenv("YOUR_NAME")
YOUR_ADDRESS = os.getenv("YOUR_ADDRESS")
YOUR_CITY_STATE_ZIP = os.getenv("YOUR_CITY_STATE_ZIP")
YOUR_EMAIL = os.getenv("YOUR EMAIL")
YOUR_PHONE_NUMBER = os.getenv("YOUR_PHONE_NUMBER")

# Application specific details

FEDERAL_WORK_STUDY = os.getenv('FEDERAL_WORK_STUDY')
ARE_YOU_BEING_REFERRED = os.getenv("ARE_YOU_BEING_REFERRED")
REFERRED_BY = os.getenv("REFERRED_BY")

def generate_payload(url):
    payload ={"partnerId":"","siteId":"","jobid":"","configMode":"","jobSiteId":"","turnOffHttps":"false"}
    parsed_url = urlparse(url)

    # Extract the query string parameters
    query_params = parse_qs(parsed_url.query)

    # Extract the fragment (everything after the '#')
    fragment = parsed_url.fragment

    # Extract values
    partnerid = query_params.get('partnerid', [None])[0]
    siteid = query_params.get('siteid', [None])[0]

    # Extract jobDetailsId from the fragment
    job_details_id = None
    if 'jobDetails=' in fragment:
        job_details_id = fragment.split('=')[1].split('_') 
    payload["jobid"]=job_details_id[0]
    payload['jobSiteId']=job_details_id[1]
    payload['siteId'] = siteid
    payload['partnerId']=partnerid

    return payload

def extract_job_information(json_data):
    job_details = json_data['ServiceResponse']['Jobdetails']['JobDetailQuestions']
    extracted_info = {
        'job_id': None,
        'job_title' : None,
        'job_designation': None,
        'job_description': None,
        'qualifications': None
    }

    for detail in job_details:
        if detail['VerityZone'] == 'autoreq':
            extracted_info['job_id'] = detail['AnswerValue']
        elif detail['VerityZone'] == 'formtext17':
            extracted_info['job_title'] = detail['AnswerValue']
        elif detail['VerityZone'] == 'jobtitle':
            extracted_info['job_title'] = detail['AnswerValue']
        elif detail['VerityZone'] == 'jobdescription':
            extracted_info['job_description'] = detail['AnswerValue']
        elif detail['VerityZone'] == 'formtext27':  
            extracted_info['qualifications'] = detail['AnswerValue']


    return extracted_info


# Take input from user
def get_input_from_user(num_jobs=10):
    jobs_and_prompts = []
    print(f"Please enter details for {num_jobs} jobs.")
    
    # Regex pattern 
    url_pattern = r"https://sjobs\.brassring\.com/TGnewUI/Search/Home/Home\?partnerid=\d+&siteid=\d+&SID=%5E\w+#jobDetails=\d+_\d+"
    
    for i in range(num_jobs):
        while True:  
            while True:  
                print(f"\nJob {i+1}:")
                job_link = input("Enter the job link: ")
                
                
                if not re.match(url_pattern, job_link):
                    print("Invalid URL format. Please enter a URL that matches the required format.")
                else:
                    break  
            
            if any(job[0] == job_link for job in jobs_and_prompts):
                print("This job has already been added. Please enter a different link.")
            else:
                break  

        custom_prompt = input("Enter your custom prompt for this job: ")
        jobs_and_prompts.append((job_link, custom_prompt))
        
    return jobs_and_prompts


def read_resume_text(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        return file.read()

    # Define the path to the 'resumes' folder and the 'parsed_resume.txt' file
    resume_folder = os.path.join(os.getcwd(), "resumes")
    parsed_resume_path = os.path.join(resume_folder, "parsed_resume.txt")

    # Read the content of 'parsed_resume.txt'
    if os.path.exists(parsed_resume_path):
        resume_text = read_resume_text(parsed_resume_path)
        return resume_text
    else:
        print(f"Resume text file not found at {parsed_resume_path}. Please make sure the file exists.")
        exit(1)


def generate_cover_letter(your_name, your_address, your_city_state_zip, your_email, your_phone_number, job_title, job_description, job_id, job_designation, attempt=1,custom_prompt="",resume=""):

    cover_letter_folder = os.path.join(os.getcwd(), "cover_letters")  # 'cover letters' is the folder name in your working directory

    print(job_id)
    cover_letter_file_name = f"{job_id}.docx"
    cover_letter_file_path = os.path.join(cover_letter_folder, cover_letter_file_name)

    if os.path.exists(cover_letter_file_path):
        print(f"Cover letter for job exists already {cover_letter_file_path}")
        return

    client = OpenAI(api_key=OPENAI_API_KEY)

    current_date = datetime.today().strftime('%B %d, %Y')

    # Prepare the prompt with job and personal details
    prompt = f"""
    You are an assistant skilled in writing professional cover letters. Please write a cover letter for the following job using the provided personal and job details:

    Personal Details:
    Name: {your_name}
    Address: {your_address}
    City/State/Zip: {your_city_state_zip}
    Email: {your_email}
    Phone Number: {your_phone_number}

    Date: {current_date}

    Job Details:
    Job Title: {job_title}
    Job ID: {job_id}
    Job Designation: {job_designation}
    Job Description: {job_description}

    Do not assume anything, stick the content matching my resume and job description.Please make sure no edits are required like brackets shouldn't exist and no extra text other than content of the cover letter. this should be the final cover letter and try to find the department name i am applying to based on the job description and keep it arizona state university,tempe,arizona,85281. Also try to include {custom_prompt}. Rerun the cover letter again to see to make sure no edits are required. this is very important. Tailor the cover letter to my resume that is {resume}
    """

    try:
        # OpenAI API call 
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful assistant."}, 
                      {"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000,  # Adjusted max_tokens to ensure full cover letter generation
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )

        # Extracting the generated text from the response
        generated_cover_letter = response.choices[0].message.content

    except RateLimitError as e:
        if attempt <= 3:  # Set a maximum number of retries
            delay = 2 ** attempt  # Exponential backoff
            print(f"Rate limit exceeded, retrying after {delay} seconds...")
            time.sleep(delay)
            return generate_cover_letter(your_name, your_address, your_city_state_zip, your_email, your_phone_number, job_title, job_description, job_id, job_designation, attempt + 1,resume)
        else:
            print("Max retry attempts reached. Failed to generate cover letter.")
            return None

    # Returning the generated cover letter directly
    return generate_document_from_prompt(generated_cover_letter,job_id)


def generate_document_from_prompt(prompt, document_id, folder_name='cover_letters'):
    # Get the current working directory
    cwd = os.getcwd()

    # Construct the full path for the folder
    base_path = os.path.join(cwd, folder_name)

    # Check if the directory exists, and create it if it doesn't
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    # Construct the filename using the document ID
    file_name = f"{document_id}.docx"
    file_path = os.path.join(base_path, file_name)

    # Create a new Document
    doc = Document()
    
    # Add the prompt (which serves as the main body) to the document
    doc.add_paragraph(prompt)
    
    # Save the document
    doc.save(file_path)

    print(f'Document saved as "{file_path}"')



num_of_jobs = int(input("How many jobs do you want to apply today: Max is 10 now :(\n"))
while(num_of_jobs<1):
    if(num_of_jobs<0):
        print("BRUH FR?!!!. No way you entered a negative number :insert skull emoji:")
    elif(num_of_jobs==0):
        print("Guess who is not getting employed anytime soon lmao")
    exit(-1)
jobs = get_input_from_user(num_of_jobs)




chrome_options = Options()
chrome_options.add_experimental_option("detach", True)


svc = webdriver.ChromeService(executable_path=binary_path)
driver = webdriver.Chrome(service=svc,options=chrome_options)

driver.get("https://students.asu.edu/employment/search")

wait = WebDriverWait(driver,60)
on_campus_button = driver.find_element(by=By.XPATH,value="/html/body/div/div/main/div[2]/article/div[2]/div/div/div/div/div/div[4]/div/a[1]")

on_campus_button.click()

username_locator = (By.XPATH,"//*[@id='username']")
password_locator = driver.find_element(by=By.XPATH,value="//*[@id='password']")

WebDriverWait(driver,10).until(
    EC.presence_of_element_located(username_locator)
)
username_locator = driver.find_element(by=By.XPATH,value="//*[@id='username']")

username_locator.send_keys(ASU_USERNAME)
password_locator.send_keys(ASU_PASSWORD)
remember_me_locator = driver.find_element(by=By.XPATH,value="//*[@id='rememberid']")
remember_me_locator.click()

submit_locator = driver.find_element(by=By.XPATH,value='/html/body/div/div/main/div/div/div/div/form/section[2]/div[1]/input')

submit_locator.click()


sign_out_locator = (By.XPATH,'/html/body/div[2]/div[2]/div[1]/div[3]/div/div[2]/nav/a[7]/span')

WebDriverWait(driver,40).until(EC.presence_of_element_located(sign_out_locator))

print("Fully loaded")
print(jobs)

for job_link, custom_prompt in jobs:

    print(f"Processing job link: {job_link} with custom prompt: \"{custom_prompt}\"")
    cookies = driver.get_cookies()
    selenium_cookies = {cookie['name']: cookie['value'] for cookie in cookies}
    url = 'https://sjobs.brassring.com/TgNewUI/Search/Ajax/JobDetails'

    # Make the POST request with cookies and payload

    # payload ={"partnerId":"25620","siteId":"5495","jobid":"4898486","configMode":"","jobSiteId":"5495","turnOffHttps":"false"}
    payload = generate_payload(job_link)
    response = requests.post(url, json=payload, cookies=selenium_cookies)

    # Parse the JSON response
    json_response = response.json()
    extracted_json = extract_job_information(json_response)
    time.sleep(2)
    driver.get(job_link)


    resume_folder = os.path.join(os.getcwd(),"resumes")
    RESUME_FILE_NAME = os.getenv("RESUME_FILE_NAME")
    resume_file_path = os.path.join(resume_folder,RESUME_FILE_NAME)
    if(os.path.exists(resume_file_path)):
        resume_text = read_resume_text(os.path.join(resume_folder,"parsed_resume.txt"))
    else:
        print(f"Dear Human, you had made one good decision in life by downloading this script, but you messed up in putting the resume into the right path or you messed up the env file")
        print(f"Its alright i give you another chance to fix your mistakes. lessgoo i believe in you. You got this!!")
        exit(5)
    
    generate_cover_letter(attempt=1, your_name=YOUR_NAME,your_address=YOUR_ADDRESS,your_city_state_zip=YOUR_CITY_STATE_ZIP,your_email=YOUR_EMAIL,your_phone_number=YOUR_PHONE_NUMBER,job_title=extracted_json['job_title'],job_id=extracted_json['job_id'],job_designation=extracted_json['job_designation'],job_description=extracted_json["job_description"],custom_prompt=custom_prompt,resume=resume_text)
    time.sleep(2)


    apply_button = (By.XPATH,'//*[@id="applyFromDetailBtn"]')
    WebDriverWait(driver,60).until(EC.presence_of_element_located(
        apply_button
    ))
    apply_button_element = driver.find_element(by=By.XPATH,value='/html/body/div[2]/div[2]/div[1]/div[7]/div[4]/div[2]/div/div[3]/div/div/div/div/button[1]')

    apply_button_element.click()
    lets_get_started_locator = (By.XPATH,'/html/body/div[2]/div[2]/div[1]/div[7]/div[3]/form/div/div[1]/div[4]/button')

    WebDriverWait(driver,60).until(EC.presence_of_element_located(
        lets_get_started_locator
    ))

    lets_get_started_button = driver.find_element(by=By.XPATH,value='/html/body/div[2]/div[2]/div[1]/div[7]/div[3]/form/div/div[1]/div[4]/button')
    lets_get_started_button.click()

    save_and_continue_locator = (By.CSS_SELECTOR,'#shownext')

    WebDriverWait(driver,60).until(EC.presence_of_element_located(
        save_and_continue_locator
    ))
    save_and_continue_button = driver.find_element(by=By.CSS_SELECTOR,value='#shownext')
    save_and_continue_button.click()

    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#radio-61829-Yes')))
    

    federal_yes = driver.find_element(by=By.CSS_SELECTOR,value='#radio-61829-Yes')
    federal_no = driver.find_element(by=By.CSS_SELECTOR,value='#radio-61829-No')


    if FEDERAL_WORK_STUDY.lower() == 'yes':
        federal_yes.click()
    else:
        federal_no.click()

    authorized = driver.find_element(By.CSS_SELECTOR,'#radio-44674-Yes')
    authorized.click()

    dropdown_menu_locator = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[2]/div[2]/div[1]/div[7]/div[3]/form/div/div[1]/div[2]/div/div/div/div/div/div[7]/span[2]/span[2]')))
    dropdown_menu = driver.find_element(by=By.XPATH,value='/html/body/div[2]/div[2]/div[1]/div[7]/div[3]/form/div/div[1]/div[2]/div/div/div/div/div/div[7]/span[2]/span[2]')
    dropdown_menu.click()

    # How did you find out about this job?

    if ARE_YOU_BEING_REFERRED.lower() == 'yes':
        referral_option = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[2]/div[2]/div[1]/div[7]/div[5]/div[1]/ul/li[6]/div')))
        referral_option.click()

        referrer_name = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[2]/div[2]/div[1]/div[7]/div[3]/form/div/div[1]/div[2]/div/div/div/div/div/div[10]/div/input')))
        referrer_name.clear()
        referrer_name.send_keys(REFERRED_BY)
    else:
        website_option = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[2]/div[2]/div[1]/div[7]/div[5]/div[1]/ul/li[4]/div')))
        website_option.click()


    save_and_continue_button = driver.find_element(by=By.XPATH,value='/html/body/div[2]/div[2]/div[1]/div[7]/div[3]/form/div/div[1]/div[4]/button')
    save_and_continue_button.click()

    time.sleep(2)

    add_resume_locator = (By.ID,'AddResumeLink')
    wait.until(EC.element_to_be_clickable(
        add_resume_locator
    ))

    add_resume_element = driver.find_element(by=By.ID,value='AddResumeLink')
    add_resume_element.click()

    resume_iframe = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div[2]")))

    resume_iframe = driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/iframe")
    driver.switch_to.frame(resume_iframe)

    upload_resume_button = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[1]/div/div/div[3]/label/input")
    

    # ADD RESUME HERE

    if os.path.exists(resume_file_path):
        upload_resume_button.send_keys(resume_file_path)
        driver.switch_to.default_content()
    else:
        print(f"You are actually fricking trolling bro!. Put the resume into {resume_folder} path and set the env variable properly")
        exit(1)
    

    add_cover_letter = (By.ID,'AddCLLink')
    wait.until(EC.element_to_be_clickable(
        add_cover_letter
    ))

    add_cover_letter_element = driver.find_element(by=By.ID,value='AddCLLink')
    add_cover_letter_element.click()

    cl_iframe = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div[2]")))

    cl_iframe = driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/iframe")
    driver.switch_to.frame(cl_iframe)

    upload_cover_letter = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[1]/div/div/div[3]/label/input")

    cover_letter_folder = os.path.join(os.getcwd(), "cover_letters")  # 'cover letters' is the folder name in your working directory
    job_id_text = extracted_json['job_id']
    print(job_id_text)
    print()
    cover_letter_file_name = f"{job_id_text}.docx"
    cover_letter_file_path = os.path.join(cover_letter_folder, cover_letter_file_name)

    print(cover_letter_file_name)
    print(cover_letter_file_path)

    if os.path.exists(cover_letter_file_path):
        if(YOLO_MODE.lower() == 'yes'):
            upload_cover_letter.send_keys(cover_letter_file_path)
        elif(YOLO_MODE.lower()=='no'):
            print(f"The file path of the cover letter you need to verify is: {cover_letter_file_path}\n")
            verify_cover_letter = input("type yes only if you are done making final changes to your cover letter. Please dont make any changes to the file name\n")
            while(verify_cover_letter.lower()!='yes'):
                print("Sir/Ma'am wtf are you doing?")
                verify_cover_letter = input("Its alright i believe in you, you know the spelling of yes for sure. or you can copy yes from this line and put it")
            upload_cover_letter.send_keys(cover_letter_file_path)
        else:
            print("Dear Human, Please read the documentation for atleast once in your lifetime. Please dont skip it like you do with terms and conditions.")
            print("Yolo mode error. Either type yes or no")
            exit(2)
    else:
        print("The cover letter wasn't generated successfully")
        print("Cover letter file does not exist:", cover_letter_file_path)
        exit(3)


    driver.switch_to.default_content()

    save_and_continue_resume_locator = wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[2]/div[2]/div[1]/div[7]/div[3]/form/div/div[1]/div[4]/button')))
    

    save_and_continue_button = driver.find_element(by=By.XPATH,value='/html/body/div[2]/div[2]/div[1]/div[7]/div[3]/form/div/div[1]/div[4]/button')
    save_and_continue_button.click()

    time.sleep(5)
    save_and_continue_after_resume = wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[2]/div[2]/div[1]/div[7]/div[3]/form/div/div[1]/div[4]/button')))
    save_and_continue_after_resume_element = driver.find_element(by=By.XPATH,value='/html/body/div[2]/div[2]/div[1]/div[7]/div[3]/form/div/div[1]/div[4]/button') 

    save_and_continue_after_resume_element.click()

    time.sleep(5)

    references_save_locator = wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[2]/div[2]/div[1]/div[7]/div[3]/form/div/div[1]/div[4]/button')))

    references_save_element = driver.find_element(by=By.XPATH,value='/html/body/div[2]/div[2]/div[1]/div[7]/div[3]/form/div/div[1]/div[4]/button')
    references_save_element.click()   

    time.sleep(5)

    gender_save_locator = wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[2]/div[2]/div[1]/div[7]/div[3]/form/div/div[1]/div[4]/button')))
    gender_save_element = driver.find_element(by=By.XPATH,value='/html/body/div[2]/div[2]/div[1]/div[7]/div[3]/form/div/div[1]/div[4]/button')
    gender_save_element.click()

    time.sleep(5)

    ethnicity_save_locator = wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[2]/div[2]/div[1]/div[7]/div[3]/form/div/div[1]/div[4]/button')))

    ethnicity_save_element = driver.find_element(by=By.XPATH,value='/html/body/div[2]/div[2]/div[1]/div[7]/div[3]/form/div/div[1]/div[4]/button')
    ethnicity_save_element.click()

    time.sleep(5)


    submit_locator = wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[2]/div[2]/div[1]/div[7]/div[3]/form/div/div[1]/div[4]/button')))
    submit_btn_element = driver.find_element(by=By.XPATH,value='/html/body/div[2]/div[2]/div[1]/div[7]/div[3]/form/div/div[1]/div[4]/button')

    submit_btn_element.click()