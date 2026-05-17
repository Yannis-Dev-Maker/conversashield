import json
import requests
import pandas as pd
from pathlib import Path


INPUT_CSV = Path("output/call_transcripts_clean.csv")
OUTPUT_CSV = Path("output/call_llm_analysis.csv")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3:12b"


def ask_gemma(prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }

    r = requests.post(OLLAMA_URL, json=payload, timeout=180)
    r.raise_for_status()

    return r.json().get("response", "").strip()


def build_prompt(row) -> str:
    return f"""
Είσαι έμπειρος QA Supervisor σε ελληνικό call center.

Αξιολόγησε την παρακάτω απομαγνητοφώνηση κλήσης.

Σκοπός:
Να ελέγξεις εάν ο Agent χειρίστηκε σωστά την κλήση, εάν ήταν ευγενικός, εάν παρουσίασε σωστά την προσφορά και εάν διαχειρίστηκε σωστά την απάντηση/ένσταση του πελάτη.

Θέλω να απαντήσεις ΜΟΝΟ σε έγκυρο JSON.
Μην γράψεις markdown.
Μην γράψεις επεξηγήσεις εκτός JSON.

Βαθμολόγηση:
- qa_score: αριθμός από 0 έως 100
- agent_passed: true εάν qa_score >= 75, αλλιώς false

Κανόνες αξιολόγησης:
1. opening_ok: Ο Agent έκανε σωστό χαιρετισμό;
2. agent_introduction_ok: Είπε όνομα ή παρουσιάστηκε;
3. company_or_campaign_ok: Είπε εταιρεία, καμπάνια ή σκοπό κλήσης;
4. offer_explained_ok: Εξήγησε καθαρά την προσφορά;
5. bank_question_ok: Ρώτησε σωστά για συνεργασία με Εθνική Τράπεζα, όπου φαίνεται σχετικό;
6. objection_handling_ok: Διαχειρίστηκε σωστά ένσταση ή άρνηση;
7. politeness_ok: Ήταν ευγενικός;
8. closing_ok: Έκλεισε σωστά την κλήση;
9. referral_attempt_ok: Ζήτησε σύσταση/referral, αν ταίριαζε στη ροή;
10. compliance_risk: true εάν υπάρχει πρόβλημα συμμόρφωσης ή παραπλανητική διατύπωση.

Schema:
{{
  "qa_score": 0,
  "agent_passed": false,
  "call_result": "successful | not_interested | already_customer | callback | wrong_number | no_meaningful_conversation | unknown",
  "opening_ok": false,
  "agent_introduction_ok": false,
  "company_or_campaign_ok": false,
  "offer_explained_ok": false,
  "bank_question_ok": false,
  "objection_handling_ok": false,
  "politeness_ok": false,
  "closing_ok": false,
  "referral_attempt_ok": false,
  "compliance_risk": false,
  "customer_objection": "",
  "agent_mistakes": [],
  "positive_points": [],
  "recommendation_to_agent": "",
  "summary": ""
}}

Κλήση:
{row.get("llm_input", "")}
""".strip()


def parse_json_safely(text: str) -> dict:
    try:
        return json.loads(text)
    except Exception:
        return {
            "summary": "",
            "call_result": "unknown",
            "customer_objection": "",
            "qa_score": "",
            "follow_up_needed": "",
            "notes": f"JSON parse error. Raw response: {text[:500]}"
        }


def main():
    df = pd.read_csv(INPUT_CSV, encoding="utf-8-sig")

    results = []

    for idx, row in df.iterrows():
        filename = row.get("filename", "")
        print(f"[{idx + 1}/{len(df)}] Analyzing: {filename}")

        prompt = build_prompt(row)

        try:
            response = ask_gemma(prompt)
            data = parse_json_safely(response)

            results.append({
                "filename": filename,
                "summary": data.get("summary", ""),
                "call_result": data.get("call_result", ""),
                "customer_objection": data.get("customer_objection", ""),
                "qa_score": data.get("qa_score", ""),
                "follow_up_needed": data.get("follow_up_needed", ""),
                "notes": data.get("notes", ""),
                "raw_llm_response": response,
            })

            print("[OK]")

        except Exception as e:
            results.append({
                "filename": filename,
                "summary": "",
                "call_result": "error",
                "customer_objection": "",
                "qa_score": "",
                "follow_up_needed": "",
                "notes": f"{type(e).__name__}: {str(e)}",
                "raw_llm_response": "",
            })

            print(f"[ERROR] {filename}: {e}")

    out_df = pd.DataFrame(results)
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    print("Done.")
    print(f"Results: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()