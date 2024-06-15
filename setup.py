import os
import shutil
import re

def validate_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email)

def validate_phone_number(phone_number):
    pattern = r"^\d{3}-\d{3}-\d{4}$"
    return re.match(pattern, phone_number)

def check_and_create_parsed_resume(filename):
    f = open(os.getcwd() + "/resumes/parsed_resume.txt", "w")

    from pypdf import PdfReader 

    # creating a pdf reader object 
    reader = PdfReader(os.getcwd()+ '/resumes/'+filename)

    # getting a specific page from the pdf file 
    page = reader.pages[0] 

    # extracting text from page 
    text = page.extract_text()
    f.write(text)
    
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
        print("Which AI model would you like to use for generating the cover letter?")
        print("1. OpenAI's ChatGPT")
        print("2. Google's Gemini")
        model_choice = int(input("Enter 1 for OpenAI's ChatGPT or 2 for Google's Gemini: "))
        if model_choice < 1 or model_choice > 2:
            print("Invalid choice. Please enter 1 or 2.")
            return
        elif model_choice == 1:
            file.write("OPENAI_API_KEY=" + get_input("Enter your OpenAI API key: ") + "\n") 
        elif model_choice == 2:
            file.write("GEMINI_API_KEY=" + get_input("Enter your Gemini Model API Key: ") + "\n")
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
        check_and_create_parsed_resume(resume_file_name)
        print("Setup complete. Resume file moved successfully.")

        print("YOLO mode is basically a mode where the program will automatically send the cover letter without asking for your confirmation. If you want to confirm the cover letter before sending, type no, Otherwise yes\n")
        
        file.write('YOLO_MODE=' + get_input('Type "yes" for YOLO mode or "no" to confirm the cover letter before sending: ') + "\n")
        

if __name__ == "__main__":
    main()
