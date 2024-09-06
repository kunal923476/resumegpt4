import openai
import re
import json
import PyPDF2
# Set up OpenAI API key
openai.api_key = 'xxxxxxxxx'

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    return '\n'.join(full_text)

# Function to read the text from a PDF file
def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        full_text = []
        for page in range(len(reader.pages)):
            full_text.append(reader.pages[page].extract_text())
    return '\n'.join(full_text)
def extract_text(file_path):
    if file_path.endswith('.docx'):
        return extract_text_from_docx(file_path)
    elif file_path.endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    else:
        raise ValueError('Unsupported file format. Please provide a DOCX or PDF file.')
def process_resume_with_genai(resume_text):
    prompt = (
        "You are an assistant extracting information from resumes. "
        "Please extract the following information in a structured format with clear labels:\n\n"
        "1. Name\n"
        "2. Email\n"
        "3. Phone number\n"
        "4. Professional Summary\n"
        "5. Work Experience (including job title, company, and dates)\n"
        "6. Education (including degree, institution, and dates)\n"
        "7. Skills (comma-separated list)\n"
        "8. Certifications (if available)\n\n"
        "Ensure that each section is clearly labeled and formatted properly. If any section is missing or not available, respond with 'Not provided'.\n\n"
        f"Resume Text: {resume_text}"
    )

    messages = [
        {"role": "system", "content": "You are a resume data extraction assistant."},
        {"role": "user", "content": prompt}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
        max_tokens=1500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    return response['choices'][0]['message']['content']
def extract_resume_details(response_text):
    details = {
        "PersonalData": {
            "Name": re.search(r'Name:\s*(.*)', response_text).group(1) if re.search(r'Name:\s*(.*)', response_text) else "Not provided",
            "Email": re.search(r'Email:\s*(.*)', response_text).group(1) if re.search(r'Email:\s*(.*)', response_text) else "Not provided",
            "Phone": re.search(r'Phone number:\s*(.*)', response_text).group(1) if re.search(r'Phone number:\s*(.*)', response_text) else "Not provided"
        },
        "ProfessionalSummary": re.search(r'Professional Summary:\s*(.*)', response_text).group(1) if re.search(r'Professional Summary:\s*(.*)', response_text) else "Not provided",
        "Experience": re.findall(r'Work Experience:\s*(.*)', response_text) or ["Not provided"],
        "Education": re.findall(r'Education:\s*(.*)', response_text) or ["Not provided"],
        "Skills": re.search(r'Skills:\s*(.*)', response_text).group(1).split(',') if re.search(r'Skills:\s*(.*)', response_text) else ["Not provided"],
        "Certifications": re.findall(r'Certifications:\s*(.*)', response_text) or ["Not provided"]
    }
    return details
def clean_extracted_details(details):
    for key, value in details.items():
        if isinstance(value, str) and value.strip() == "**":
            details[key] = "Not provided"
        elif isinstance(value, list):
            details[key] = ["Not provided" if item.strip() == "**" else item for item in value]
    return details

def save_as_json(extracted_details, output_file):
    with open(output_file, 'w') as json_file:
        json.dump(extracted_details, json_file, indent=4)
def main(file_path, output_file):
    
    resume_text = extract_text(file_path)
    genai_response = process_resume_with_genai(resume_text)
    
    extracted_details = extract_resume_details(genai_response)
    cleaned_details = clean_extracted_details(extracted_details)
    save_as_json(cleaned_details, output_file)
    print(f"Extracted resume details saved to {output_file}")

if __name__ == '__main__':
    resume_file = '/Users/binitkunal/Agent-llm/Web-Scraping-With-LLMs-/Binits Resume_moz.pdf' 
    output_json = 'extracted_resume_details.json'
    main(resume_file, output_json)
