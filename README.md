# PitchForksPilot

This project automates the application process, enabling you to fill out applications in under a minute with the help of AI that generates cover letters for you tailored to your resume and job description.


## Table of Contents
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Running the Setup Script](#running-the-setup-script)
- [Configuration](#configuration)
  - [Verifying `.env` Configuration](#verifying-env-configuration)
- [Getting Ready for takeoff](#getting-ready-for-takeoff)
- [Common Issues](#common-issues)
- [Contributing to the project](#contributing)


## Getting Started

Dear Human, please read the documentation and follow them to make sure it works as expected.**Please don't skip it like you do with Terms & Conditions**

### Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.x
- Pip (Python package installer)

### Installation

Follow these steps to get your development environment set up:

1. **Install Python**

   If Python is not already installed on your machine, download and install it from [python.org](https://www.python.org/downloads/). Follow the installation instructions for your operating system.

2. **Clone the Repository**
   Clone this repository to your local machine using the following command:

   ```bash
   git clone https://github.com/rohit-iwnl/PitchForkPilot.git
   cd PitchForkPilot
3. **Install the requirements file by**
	```bash
	pip install -r requirements.txt
### Running the Setup Script

To generate your `.env` file, run the `setup.py` script by executing the following command in your terminal:

```bash
python3 setup.py
```
## Configuration

After running the `setup.py` script to initialize your project setup, it's crucial to verify the `.env` file created in your project's root directory. The `.env` file contains essential configurations necessary for the application to run correctly. Here's what each variable in the `.env` file represents:

- `OPENAI_API_KEY`: Your OpenAI API key for accessing OpenAI services.
- `ASU_USERNAME`: Your ASU username, required for specific operations within the application.
- `ASU_PASSWORD`: Your ASU password, which is case sensitive.
- `SIGN_IN_TIMEOUT`: The timeout for sign-in operations, set to 60 seconds by default.
- `YOUR_NAME`: Your full name, used in various application forms.
- `YOUR_ADDRESS`: Your primary address line.
- `YOUR_CITY_STATE_ZIP`: Your city, state, and ZIP code, formatted as `city,state,zip`.
- `YOUR_EMAIL`: Your email address, used for communications and applications.
- `YOUR_PHONE_NUMBER`: Your phone number, formatted as `123-456-7890`.
- `FEDERAL_WORK_STUDY`: Indicates whether you are on Federal Work Study. Type "Yes" or "No".
- `ARE_YOU_BEING_REFERRED`: Indicates if you are being referred for a position. Type "Yes" or "No".
- `REFERRED_BY`: If being referred, the name of the person who referred you.
- `RESUME_FILE_NAME`: The filename of your resume stored in the `resumes` folder within the project directory.
- `YOLO_MODE`: Determines whether to skip confirmation of the cover letter before sending. Recommended to be set as "no".

### Verifying `.env` Configuration

Ensure that you review the `.env` file and confirm that all information is correct and formatted as expected. This step is crucial for the successful operation of the application. If any adjustments are needed, you can directly edit the `.env` file using a text editor.

## Getting Ready for takeoff

After you have completed the installation, setup, and configuration verification steps, you are ready to start using the application. To begin the application process, run the `pilot.py` script by executing the following command in your terminal:

```bash
python3 pilot.py
```

## Common Issues

### Rate Limit Error with OpenAI API

If you encounter a rate limit error from the OpenAI API, it means you've exceeded the number of requests allowed in a given time period. Here are steps you can take to resolve this issue:

1. **Create Another API Key**: Sometimes, simply generating a new API key from your current OpenAI account can resolve the issue. Visit the [OpenAI API keys page](https://platform.openai.com/account/api-keys) to manage and create new keys.

2. **Create a New Account**: If creating a new API key does not resolve the rate limit error, you may need to create a new OpenAI account.

### Report any other issue incase you face one by creating an issue on github, and attaching the logs to it.

## Contributing

Contributions are welcome. Whether it's fixing bugs, improving documentation, or adding new features, your contributions are greatly appreciated.

### Here's how you can contribute:
1. Fork
2. Make a branch
3. Add your contribution and commit to the branch
4. Push your local changes and submit a PR

