from fpdf import FPDF
import os

class PDFs(FPDF):
    def header(self):
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Title
        self.cell(0, 10, 'Retail Operational Intelligence - Solution Architecture', 0, 1, 'C')
        # Line break
        self.ln(10)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

    def chapter_title(self, label):
        # Arial 12
        self.set_font('Arial', 'B', 12)
        # Background color
        self.set_fill_color(200, 220, 255)
        # Title
        self.cell(0, 6, label, 0, 1, 'L', 1)
        # Line break
        self.ln(4)

    def chapter_body(self, text):
        # Times 12
        self.set_font('Times', '', 12)
        # Output justified text
        self.multi_cell(0, 10, text)
        # Line break
        self.ln()

def create_pdf(filename):
    pdf = PDFs()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # 1. Executive Summary
    pdf.chapter_title('1. Executive Summary')
    pdf.chapter_body(
        "This document outlines the technical approach to build an automated, config-driven data pipeline for the 'Retail Operational Intelligence & Personalization Suite'. "
        "The system will ingest raw inventory reports and restock logs, validate data integrity, reconcile discrepancies using fuzzy logic, and produce a high-quality 'Golden Record' of inventory."
    )
    
    # 2. Key Goals
    pdf.chapter_title('2. Key Goals & Focus Areas')
    pdf.chapter_body(
        "- Ingest daily inventory_snapshot.csv and restock_events.csv into a RAW layer.\n"
        "- Validate inventory quantities (Negative stock, Mismatched Product IDs, Duplicates, Logical Max).\n"
        "- Recompute Effective Stock Level = Snapshot + Restock - Damaged/Expired.\n"
        "- Load cleaned data into a Curated Inventory Fact Table.\n"
        "- Route invalid records to a Quarantine Table."
    )

    # 3. System Architecture
    pdf.chapter_title('3. System Architecture Strategy')
    pdf.chapter_body(
        "We implementation a 'Medallion Architecture' (Bronze -> Silver -> Gold):\n\n"
        "A. Config-Driven Ingestion (The 'Additional Score' Goal)\n"
        "To support *any* new inventory file without code changes, we abstract file definitions into a YAML Configuration system. "
        "A 'schema_config.yaml' will define file patterns and required columns. A generic reader factory will parse files based on this config.\n\n"
        "B. Validation & Quarantine Logic\n"
        "We implement a validation pipeline. Records failing checks (e.g., negative stock) are tagged and moved to a Quarantine dataset, while valid records proceed to the Silver layer."
    )

    # 4. Reconciliation Engine
    pdf.chapter_title('4. Inventory Reconciliation Engine (Fuzzy Matching)')
    pdf.chapter_body(
        "For records quarantined due to 'Mismatched Product ID', we run a recovery process:\n"
        "1. Identify records where product_id does not exist in Master Data.\n"
        "2. Use Levenshtein Distance (Fuzzy Matching) to compare names against the Master Catalog.\n"
        "3. If Match Score > 90%: Auto-map and move to Silver Layer.\n"
        "4. If Match Score < 90%: Keep in Quarantine for manual review."
    )

    # 5. Technical Stack
    pdf.chapter_title('5. Technical Stack Recommendation')
    pdf.chapter_body(
        "Language: Python 3.10+\n"
        "Data Processing: Polars (for performance) or Pandas\n"
        "Database: DuckDB (Serverless SQL OLAP)\n"
        "Fuzzy Matching: rapid_fuzz or thefuzz\n"
        "Orchestration: Python script (main.py) with modular design."
    )
    
    pdf.output(filename, 'F')
    print(f"PDF generated successfully: {filename}")

if __name__ == "__main__":
    output_path = r"C:/Users/91823/.gemini/antigravity/brain/8f155d49-b9ca-49ba-bcb8-3c7db8ff8b32/Solution_Architecture.pdf"
    try:
        create_pdf(output_path)
    except Exception as e:
        print(f"Error generating PDF: {e}")
