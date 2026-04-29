from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq


class ReportAnalyzer:
    def __init__(self, medical_report):
        self.medical_report = medical_report

        self.model = ChatGroq(
            api_key="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",
            model="llama-3.3-70b-versatile",
            temperature=0.0
        )

        self.prompt_template = PromptTemplate.from_template("""
You are a professional clinical report analyzer.

Analyze the given medical report and generate a structured, formal medical analysis.

STRICT RULES:
- Do NOT assume any medical specialty unless clearly mentioned.
- Do NOT generate information not present in the report.
- Keep the tone formal and clinical.
- If data is missing, do not guess.

FORMAT:

CLINICAL LABORATORY ANALYSIS REPORT

--------------------------------------------

1. KEY FINDINGS:
- List only abnormal or important findings
- If none, write: No significant abnormalities detected

--------------------------------------------

2. OBSERVATIONS:
Parameter | Value | Reference Range | Interpretation

(Include only available parameters)

--------------------------------------------

3. CLINICAL INTERPRETATION:
Write a short professional paragraph explaining findings.

--------------------------------------------

4. IMPRESSION:
Short summary of overall findings.

--------------------------------------------

5. RECOMMENDATIONS:
- Suggest further tests if needed
- Suggest doctor consultation
- Do NOT suggest medicines

--------------------------------------------

6. DISCLAIMER:
This report is AI-generated and should be clinically verified.

--------------------------------------------

Medical Report:
{medical_report}
""")

    def run(self):
        try:
            prompt = self.prompt_template.format(
                medical_report=self.medical_report
            )
            response = self.model.invoke(prompt)
            return response.content

        except Exception as e:
            print("Error:", e)
            return "Error generating report."
