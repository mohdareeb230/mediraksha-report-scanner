from flask import Flask, request, render_template
from concurrent.futures import ThreadPoolExecutor, as_completed
from Utils.Agent import Cardiologist, Psychologist, Pulmonologist, MultidisciplinaryTeam
import os
import pdfplumber 

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
RESULT_PATH = 'results/final_diagnosis.txt'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(RESULT_PATH), exist_ok=True)


def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('report')

        if file:
            try:
                filename = file.filename.lower()

                
                if filename.endswith('.txt'):
                    medical_report = file.read().decode('utf-8', errors='replace')

                
                elif filename.endswith('.pdf'):
                    medical_report = extract_text_from_pdf(file)

                else:
                    return render_template("index.html", error="Please upload a valid .txt or .pdf file.")

                # Normalize text (important for LLMs)
                medical_report = medical_report.encode("utf-8", errors="ignore").decode("utf-8")

                # Run individual specialists
                agents = {
                    "Cardiologist": Cardiologist(medical_report),
                    "Psychologist": Psychologist(medical_report),
                    "Pulmonologist": Pulmonologist(medical_report)
                }

                responses = {}
                with ThreadPoolExecutor() as executor:
                    futures = {executor.submit(agent.run): name for name, agent in agents.items()}
                    for future in as_completed(futures):
                        agent_name = futures[future]
                        responses[agent_name] = future.result()

                # Run multidisciplinary agent
                team_agent = MultidisciplinaryTeam(
                    cardiologist_report=responses["Cardiologist"],
                    psychologist_report=responses["Psychologist"],
                    pulmonologist_report=responses["Pulmonologist"]
                )
                final_diagnosis = team_agent.run()

                # Save result
                final_diagnosis_text = final_diagnosis
                with open(RESULT_PATH, 'w', encoding='utf-8') as result_file:
                    result_file.write(final_diagnosis_text)

                return render_template("index.html", diagnosis=final_diagnosis_text)

            except Exception as e:
                return render_template("index.html", error=f"Error processing file: {str(e)}")

        return render_template("index.html", error="No file uploaded.")

    return render_template("index.html")


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
