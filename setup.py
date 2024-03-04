def validate_email(email):
    import re
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email)

def validate_phone_number(phone_number):
    import re
    pattern = r"^\d{3}-\d{3}-\d{4}$"
    return re.match(pattern, phone_number)

def get_input(prompt, validation_function=None):
    while True:
        user_input = input(prompt)
        if validation_function:
            if validation_function(user_input):
                return user_input
            else:
                print("Invalid input. Please try again.")
        else:
            return user_input

def main():
    with open(".env", "w") as file:
        file.write("OPENAI_API_KEY=" + get_input("Enter your OpenAI API key: ") + "\n")
        file.write("ASU_USERNAME=" + get_input("Enter your ASU username: ") + "\n")
        file.write("ASU_PASSWORD=" + get_input("Enter your ASU password (case sensitive): ") + "\n")
        file.write("SIGN_IN_TIMEOUT=" + get_input("Enter sign in timeout: ") + "\n")
        file.write("YOUR_NAME=" + get_input("Enter your full name: ") + "\n")
        file.write("YOUR_ADDRESS=" + get_input("Enter your address line 1: ") + "\n")
        file.write("YOUR_CITY_STATE_ZIP=" + get_input("Enter your city, state, and zip code (format: city,state,zip): ") + "\n")
        file.write("YOUR_EMAIL=" + get_input("Enter your email: ", validate_email) + "\n")
        file.write("YOUR_PHONE_NUMBER=" + get_input("Enter your phone number (format: 123-456-7890): ", validate_phone_number) + "\n")
        file.write('FEDERAL_WORK_STUDY="' + get_input('Type "Yes" or "No" for Federal Work Study: ') + '"\n')
        file.write('ARE_YOU_BEING_REFERRED="' + get_input('Type "Yes" or "No" if you are being referred: ') + '"\n')
        referred_by_input = 'REFERRED_BY='
        referred_by_input += get_input("Enter the name of the person who referred you: ")
        file.write(referred_by_input + "\n")
        file.write("RESUME_FILE_NAME=" + get_input("Enter the name of your resume file: ") + "\n")
        file.write('YOLO_MODE=' + get_input('Type "yes" for YOLO mode or "no" to confirm the cover letter before sending: ') + "\n")

if __name__ == "__main__":
    main()
