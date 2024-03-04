import os
import shutil
import re

def validate_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email)

def validate_phone_number(phone_number):
    pattern = r"^\d{3}-\d{3}-\d{4}$"
    return re.match(pattern, phone_number)

def check_and_create_parsed_resume():
    destination_folder = os.path.join(os.getcwd(), "resumes")
    parsed_resume_path = os.path.join(destination_folder, "parsed_resume.txt")
    
    print("\nPlease create a file named 'parsed_resume.txt' in the resumes folder and paste your resume in plain text into this file.")
    while True:
        check = input("\nAfter pasting your plain text resume into 'parsed_resume.txt', type 'yes' and press Enter to continue: ")
        if check.lower() == "yes":
            if os.path.isfile(parsed_resume_path):  
                print("Parsed resume file detected. Continuing with setup...")
                break  
            else:
                print("Parsed resume file not detected. Please make sure the file is created in the 'resumes' folder and contains your resume.")
        else:
            print("Please type 'yes' and press Enter after you have pasted your resume in plain text into 'parsed_resume.txt'.")
            print("This is to ensure no formatting or encoding errors occur when the program reads your resume for tailoring the cover letter.")

def file_exists(filename):
    return os.path.isfile(filename)

def move_file_to_resumes(filename):
    destination_folder = os.path.join(os.getcwd(), "resumes")
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    shutil.move(filename, os.path.join(destination_folder, os.path.basename(filename)))

def get_input(prompt, validation_function=None):
    while True:
        user_input = input(prompt)
        if validation_function:
            if callable(validation_function) and not validation_function(user_input):
                print("Invalid input. Please try again.")
            elif validation_function == file_exists and not file_exists(user_input):
                print("File does not exist. Please enter a valid file name.")
            else:
                return user_input
        else:
            return user_input

def main():
    with open(".env", "w") as file:
        file.write("OPENAI_API_KEY=" + get_input("Enter your OpenAI API key: ") + "\n")
        file.write("ASU_USERNAME=" + get_input("Enter your ASU username: ") + "\n")
        file.write("ASU_PASSWORD=" + get_input("Enter your ASU password (case sensitive): ") + "\n")
        file.write("SIGN_IN_TIMEOUT=60" + "\n")
        file.write("YOUR_NAME=" + get_input("Enter your full name: ") + "\n")
        file.write("YOUR_ADDRESS=" + get_input("Enter your address line 1: ") + "\n")
        file.write("YOUR_CITY_STATE_ZIP=" + get_input("Enter your city, state, and zip code (format: city,state,zip): ") + "\n")
        file.write("YOUR_EMAIL=" + get_input("Enter your email: ", validate_email) + "\n")
        file.write("YOUR_PHONE_NUMBER=" + get_input("Enter your phone number (format: 123-456-7890): ", validate_phone_number) + "\n")
        file.write('FEDERAL_WORK_STUDY="' + get_input('Type "Yes" or "No" for Federal Work Study: ') + '"\n')
        file.write('ARE_YOU_BEING_REFERRED="' + get_input('Type "Yes" or "No" if you are being referred: ') + '"\n')
        referred_by_input = 'REFERRED_BY="'
        referred_by_input += get_input("Enter the name of the person who referred you: ")
        referred_by_input += '"'
        file.write(referred_by_input + "\n")
        
        resume_file_name = get_input("Enter the name of your resume file (make sure it's in the current directory): ", file_exists)
        move_file_to_resumes(resume_file_name)
        file.write("RESUME_FILE_NAME=" + resume_file_name + "\n")
        check_and_create_parsed_resume()
        
        file.write('YOLO_MODE=' + get_input('Type "yes" for YOLO mode or "no" to confirm the cover letter before sending: ') + "\n")
        
        print("Setup complete. Resume file moved successfully.")

if __name__ == "__main__":
    main()
