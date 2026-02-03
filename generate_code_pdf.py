from fpdf import FPDF
import os

class PDFs(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Pipeline Core Code Explanation', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

    def chapter_title(self, label):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 6, label, 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, text):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 6, text)
        self.ln()

    def code_block(self, code):
        self.set_font('Courier', '', 10)
        self.set_fill_color(240, 240, 240)
        self.multi_cell(0, 5, code, 0, 'L', True)
        self.ln()

def create_explanation_pdf(filename):
    pdf = PDFs()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Intro
    pdf.chapter_body(
        "This document provides a detailed breakdown of 'pipeline/src/pipeline_core.py'. "
        "After refactoring, this file contains specialized helper functions that power the extraction, configuration, and validation logic of the pipeline."
    )
    
    # 1. Configuration
    pdf.chapter_title('1. Configuration Section')
    pdf.chapter_body("These functions handle reading the YAML instructions which define the validation rules.")
    
    pdf.code_block(
        "def load_config(config_path: str) -> Dict:\n"
        "    with open(config_path, 'r') as f:\n"
        "        return yaml.safe_load(f)"
    )
    pdf.chapter_body(
        "- What it does: Opens 'schema_config.yaml' and converts it into a Python Dictionary.\n"
        "- Why: Allows the pipeline to know rules dynamically without hardcoding them."
    )

    pdf.code_block(
        "def get_dataset_config(config: Dict, dataset_name: str) -> Dict:\n"
        "    return config['datasets'].get(dataset_name)"
    )
    pdf.chapter_body(
        "- What it does: Retrieves specific rules for a dataset (e.g., 'inventory_snapshot').\n"
        "- Why: Different files have different columns and integrity requirements."
    )

    # 2. Ingestion
    pdf.chapter_title('2. Ingestion Section')
    pdf.chapter_body("This function handles the raw data loading.")
    
    pdf.code_block(
        "def load_csv(data_dir: str, filename: str) -> pd.DataFrame:\n"
        "    path = os.path.join(data_dir, filename)\n"
        "    if not os.path.exists(path):\n"
        "        raise FileNotFoundError(f'File not found: {path}')\n"
        "    return pd.read_csv(path)"
    )
    pdf.chapter_body(
        "- What it does: Constructs the full path and reads the CSV into a Pandas DataFrame.\n"
        "- Safety: Checks file existence first to provide clear error messages."
    )

    # 3. Validation
    pdf.chapter_title('3. Validation Logic (The Brain)')
    pdf.chapter_body(
        "This is the core filter of the system. It splits data into 'Good' (Valid) and 'Bad' (Quarantine) streams."
    )
    pdf.code_block(
        "def validate_data(df: pd.DataFrame, rules: Dict, master_products: set) -> Tuple..."
    )
    pdf.chapter_body(
        "Key Steps inside this function:\n\n"
        "A. Quarantine Mask:\n"
        "   Creates a boolean series (True/False) for every row. Initially all are False (Valid).\n\n"
        "B. Rule Loop:\n"
        "   Loops through columns defined in YAML. If a check like 'min_0' is found, it marks rows with values < 0 as True (Invalid) in the mask.\n\n"
        "C. Master Data Check:\n"
        "   Checks if 'product_id' exists in the master list. If not, marks row as Invalid.\n\n"
        "D. Splitting:\n"
        "   quarantine_df = df[quarantine_mask]\n"
        "   valid_df = df[~quarantine_mask]\n"
        "   The '~' operator inverts the mask to select only the valid rows."
    )

    pdf.output(filename, 'F')
    print(f"PDF generated: {filename}")

if __name__ == "__main__":
    output_path = r"C:/Users/91823/.gemini/antigravity/brain/8f155d49-b9ca-49ba-bcb8-3c7db8ff8b32/Pipeline_Core_Explanation.pdf"
    try:
        create_explanation_pdf(output_path)
    except Exception as e:
        print(f"Error: {e}")
