from flask import Flask, request, render_template
from Utils.Agent import ReportAnalyzer
import os
import pdfplumber
print("API KEY:", os.getenv("GROQ_API_KEY"))
app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
RESULT_PATH = 'results/final_report.txt'

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
                    return render_template("index.html", error="Upload .txt or .pdf file only.")

                medical_report = medical_report.encode("utf-8", errors="ignore").decode("utf-8")

                # Use single analyzer
                analyzer = ReportAnalyzer(medical_report)
                final_report = analyzer.run()

                # Save output
                with open(RESULT_PATH, 'w', encoding='utf-8') as f:
                    f.write(final_report)

                return render_template("index.html", diagnosis=final_report)

            except Exception as e:
                return render_template("index.html", error=str(e))

        return render_template("index.html", error="No file uploaded.")

    return render_template("index.html")


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
