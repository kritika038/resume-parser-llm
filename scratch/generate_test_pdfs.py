import os
from reportlab.pdfgen import canvas

def make_pdf(filename, name, text_lines):
    # Ensure directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    c = canvas.Canvas(filename)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(80, 750, name)
    c.setFont("Helvetica", 10)
    y = 710
    for line in text_lines:
        if line.startswith("===") or line.startswith("EDUCATION") or line.startswith("SKILLS") or line.startswith("EXPERIENCE"):
            c.setFont("Helvetica-Bold", 12)
            y -= 10
            c.drawString(80, y, line)
            c.setFont("Helvetica", 10)
        else:
            c.drawString(80, y, line)
        y -= 18
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = 750
    c.save()

if __name__ == "__main__":
    # 1. ALICE DEV (Perfect fit)
    alice_lines = [
        "Email: alice.dev@gmail.com | Phone: +1 555-0199",
        "LinkedIn: linkedin.com/in/alicedev | GitHub: github.com/alicedev",
        "============================================================",
        "EDUCATION",
        "- M.S. in Software Engineering, Stanford University (2022)",
        "- B.S. in Computer Science, UC Berkeley (2020)",
        "============================================================",
        "SKILLS",
        "- Languages: Python, SQL, JavaScript",
        "- Frameworks & AI: PyTorch, LangChain, Sentence Transformers, FastAPI",
        "- Tools: Docker, Kubernetes, AWS, Git, GitHub, CI/CD",
        "============================================================",
        "EXPERIENCE",
        "Senior Software Engineer | TechCorp Inc. (2022 - Present)",
        "- Architected high-throughput RAG search platform using Sentence Transformers",
        "- Implemented microservices using FastAPI, Docker, and Kubernetes on AWS",
        "- Designed CI/CD pipelines to automate deployment workflows"
    ]
    make_pdf("scratch/Alice_Dev.pdf", "Alice Dev", alice_lines)

    # 2. BOB CODER (Frontend/basic fit)
    bob_lines = [
        "Email: bob.coder@yahoo.com | Phone: +1 555-0144",
        "============================================================",
        "EDUCATION",
        "- B.S. in Information Technology, Arizona State University (2023)",
        "============================================================",
        "SKILLS",
        "- Languages: JavaScript, HTML, CSS",
        "- Tools: Git, GitHub, VS Code",
        "============================================================",
        "EXPERIENCE",
        "Junior Developer | WebCrafters Studio (2023 - Present)",
        "- Built responsive user interfaces and interactive dashboards",
        "- Handled state management and API integrations using JavaScript",
        "- Maintained version control using Git and GitHub workflows"
    ]
    make_pdf("scratch/Bob_Coder.pdf", "Bob Coder", bob_lines)

    # 3. CHARLIE ML (ML research fit)
    charlie_lines = [
        "Email: charlie.ml@outlook.com | Phone: +1 555-0177",
        "============================================================",
        "EDUCATION",
        "- Ph.D. in Machine Learning, MIT (2024)",
        "============================================================",
        "SKILLS",
        "- Languages: Python, SQL",
        "- AI/ML: PyTorch, Deep Learning, Sentence Transformers, NLP, spaCy",
        "- Tools: Git, Jupyter Notebooks, AWS (EC2)",
        "============================================================",
        "EXPERIENCE",
        "AI Research Assistant | MIT CSAIL (2020 - 2024)",
        "- Trained custom Sentence Transformers models for dense semantic search",
        "- Applied deep learning frameworks for natural language processing",
        "- Managed model evaluations and preprocessed large-scale datasets"
    ]
    make_pdf("scratch/Charlie_ML.pdf", "Charlie ML", charlie_lines)

    print("Success: Generated Alice_Dev.pdf, Bob_Coder.pdf, and Charlie_ML.pdf in scratch/")
