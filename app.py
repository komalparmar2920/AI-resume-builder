# app.py
from flask import (
    Flask,
    render_template,
    request,
    send_file,
    url_for,
    redirect,
    session,
    jsonify,
)
from fpdf import FPDF
from io import BytesIO
import os

# import random
# import string
# import base64
from werkzeug.utils import secure_filename
import datetime


app = Flask(__name__)
app.secret_key = "jnjnjknknvgfcfxm"


# Create upload folder if it doesn't exist
UPLOAD_FOLDER = "static/uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg", "gif"}

# Canva-inspired templates
TEMPLATES = {
    "modern_minimal": {
        "name": "Modern Minimal",
        "color": "#2E5090",
        "accent_color": "#E8EBF2",
        "font": "Helvetica",
        "header_style": "clean",
        "layout": "sidebar",
        "preview_img": "modern_minimal.png",
    },
    "bold_creative": {
        "name": "Bold Creative",
        "color": "#D92B2B",
        "accent_color": "#F9E9E9",
        "font": "Helvetica",
        "header_style": "boxed",
        "layout": "full",
        "preview_img": "bold_creative.png",
    },
    "elegant_pro": {
        "name": "Elegant Professional",
        "color": "#2B7D6A",
        "accent_color": "#E8F4F1",
        "font": "Times",
        "header_style": "underlined",
        "layout": "sidebar",
        "preview_img": "elegant_pro.png",
    },
    "tech_modern": {
        "name": "Tech Modern",
        "color": "#333333",
        "accent_color": "#F0F0F0",
        "font": "Helvetica",
        "header_style": "clean",
        "layout": "full",
        "preview_img": "tech_modern.png",
    },
    "creative_colorful": {
        "name": "Creative Colorful",
        "color": "#8C52FF",
        "accent_color": "#F1EBFF",
        "font": "Helvetica",
        "header_style": "boxed",
        "layout": "sidebar",
        "preview_img": "creative_colorful.png",
    },
}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


class CanvaResumeGenerator:
    def __init__(self, template_id):
        self.template_id = template_id
        self.template_data = TEMPLATES[template_id]
        self.pdf = FPDF()
        self.pdf.add_page()

        # Set up variables based on template
        self.primary_color = self.hex_to_rgb(self.template_data["color"])
        self.accent_color = self.hex_to_rgb(self.template_data["accent_color"])
        self.font = self.template_data["font"]
        self.header_style = self.template_data["header_style"]
        self.layout = self.template_data["layout"]

        # Initialize dimensions based on layout
        if self.layout == "sidebar":
            self.sidebar_width = 60
            self.content_x = self.sidebar_width + 5
            self.content_width = 210 - self.content_x - 10

            # Draw sidebar background
            self.pdf.set_fill_color(*self.accent_color)
            self.pdf.rect(0, 0, self.sidebar_width, 297, style="F")
        else:
            self.content_x = 10
            self.content_width = 190

    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        h = hex_color.lstrip("#")
        return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))

    def add_photo(self, photo_path):
        """Add photo based on template layout"""
        if photo_path and os.path.exists(photo_path):
            if self.layout == "sidebar":
                # Center in sidebar
                self.pdf.image(photo_path, x=5, y=20, w=self.sidebar_width - 10, h=50)
            else:
                # Top right for full layout
                self.pdf.image(photo_path, x=160, y=10, w=30, h=30)

    def add_header(self, name, email, phone, has_photo=False):
        """Add header with styling based on template"""
        if self.layout == "sidebar":
            # Name in main content
            self.pdf.set_font(self.font, "B", 24)
            self.pdf.set_text_color(*self.primary_color)
            self.pdf.set_xy(self.content_x, 20)
            self.pdf.cell(self.content_width, 15, name, ln=True)

            # Contact in sidebar
            self.pdf.set_font(self.font, "", 10)
            self.pdf.set_text_color(50, 50, 50)
            y_position = 80 if has_photo else 30

            # Draw contact info in sidebar
            self.pdf.set_xy(5, y_position)
            self.pdf.cell(self.sidebar_width - 10, 7, "CONTACT", ln=True)

            self.pdf.set_font(self.font, "", 9)
            self.pdf.set_xy(5, y_position + 10)
            self.pdf.cell(self.sidebar_width - 10, 6, email, ln=True)
            self.pdf.set_xy(5, y_position + 16)
            self.pdf.cell(self.sidebar_width - 10, 6, phone, ln=True)

            # Add decorative element based on header style
            if self.header_style == "underlined":
                self.pdf.set_xy(self.content_x, 35)
                self.pdf.set_draw_color(*self.primary_color)
                self.pdf.set_line_width(0.5)
                self.pdf.line(self.content_x, 36, self.content_x + 100, 36)
            elif self.header_style == "boxed":
                self.pdf.set_xy(self.content_x - 2, 18)
                self.pdf.set_draw_color(*self.primary_color)
                self.pdf.set_line_width(0.5)
                self.pdf.rect(self.content_x - 2, 18, 102, 18)
        else:
            # Full layout
            if self.header_style == "boxed":
                # Draw header box
                self.pdf.set_fill_color(*self.accent_color)
                self.pdf.rect(0, 0, 210, 40, style="F")

                # Add name
                self.pdf.set_font(self.font, "B", 24)
                self.pdf.set_text_color(*self.primary_color)
                self.pdf.set_xy(10, 10)
                self.pdf.cell(150 if has_photo else 190, 15, name, ln=True)

                # Add contact info
                self.pdf.set_font(self.font, "", 11)
                self.pdf.set_text_color(50, 50, 50)
                self.pdf.set_xy(10, 25)
                self.pdf.cell(
                    150 if has_photo else 190,
                    7,
                    f"Email: {email} | Phone: {phone}",
                    ln=True,
                )
            else:
                # Simple header
                self.pdf.set_font(self.font, "B", 24)
                self.pdf.set_text_color(*self.primary_color)
                self.pdf.set_xy(10, 10)
                self.pdf.cell(150 if has_photo else 190, 15, name, ln=True)

                # Add contact info
                self.pdf.set_font(self.font, "", 11)
                self.pdf.set_text_color(50, 50, 50)
                self.pdf.set_xy(10, 25)
                self.pdf.cell(
                    150 if has_photo else 190,
                    7,
                    f"Email: {email} | Phone: {phone}",
                    ln=True,
                )

                # Add decorative element if underlined
                if self.header_style == "underlined":
                    self.pdf.set_xy(10, 35)
                    self.pdf.set_draw_color(*self.primary_color)
                    self.pdf.set_line_width(0.5)
                    self.pdf.line(10, 35, 200, 35)

    def add_section_header(self, title, y_position):
        """Add styled section header"""
        if self.layout == "sidebar":
            self.pdf.set_xy(self.content_x, y_position)
        else:
            self.pdf.set_xy(10, y_position)

        self.pdf.set_font(self.font, "B", 14)
        self.pdf.set_text_color(*self.primary_color)
        self.pdf.cell(0, 10, title.upper(), ln=True)

        # Add decorative element based on header style
        if self.header_style == "underlined":
            if self.layout == "sidebar":
                self.pdf.set_xy(self.content_x, y_position + 10)
                self.pdf.set_draw_color(*self.primary_color)
                self.pdf.set_line_width(0.3)
                self.pdf.line(
                    self.content_x,
                    y_position + 10,
                    self.content_x + self.content_width - 5,
                    y_position + 10,
                )
            else:
                self.pdf.set_xy(10, y_position + 10)
                self.pdf.set_draw_color(*self.primary_color)
                self.pdf.set_line_width(0.3)
                self.pdf.line(10, y_position + 10, 200, y_position + 10)

        return y_position + 15

    def add_education(self, degree, percentage, cgpa, college, y_position):
        """Add education section"""
        y_position = self.add_section_header("EDUCATION", y_position)

        if self.layout == "sidebar":
            self.pdf.set_xy(self.content_x, y_position)
        else:
            self.pdf.set_xy(10, y_position)

        # College name
        self.pdf.set_font(self.font, "B", 12)
        self.pdf.set_text_color(0, 0, 0)
        self.pdf.cell(self.content_width, 8, college, ln=True)

        # Degree
        self.pdf.set_font(self.font, "", 11)
        y_position += 8
        if self.layout == "sidebar":
            self.pdf.set_xy(self.content_x, y_position)
        else:
            self.pdf.set_xy(10, y_position)
        self.pdf.cell(self.content_width, 6, f"Degree: {degree}", ln=True)

        # Percentage and CGPA
        y_position += 6
        if self.layout == "sidebar":
            self.pdf.set_xy(self.content_x, y_position)
        else:
            self.pdf.set_xy(10, y_position)
        self.pdf.cell(
            self.content_width, 6, f"Percentage: {percentage}% | CGPA: {cgpa}", ln=True
        )

        return y_position + 10

    def add_projects(self, projects, y_position):
        """Add projects section"""
        y_position = self.add_section_header("PROJECTS", y_position)

        project_list = projects.split(";")
        for project in project_list:
            if project.strip():
                if self.layout == "sidebar":
                    self.pdf.set_xy(self.content_x, y_position)
                else:
                    self.pdf.set_xy(10, y_position)

                project_parts = project.split(":")

                if len(project_parts) > 1:
                    # Project title
                    self.pdf.set_font(self.font, "B", 12)
                    self.pdf.set_text_color(0, 0, 0)
                    self.pdf.cell(
                        self.content_width, 8, project_parts[0].strip(), ln=True
                    )

                    # Project description
                    y_position += 8
                    if self.layout == "sidebar":
                        self.pdf.set_xy(self.content_x, y_position)
                    else:
                        self.pdf.set_xy(10, y_position)

                    self.pdf.set_font(self.font, "", 11)
                    self.pdf.multi_cell(self.content_width, 6, project_parts[1].strip())
                    y_position += self.pdf.get_y() - y_position
                else:
                    # Just project title
                    self.pdf.set_font(self.font, "B", 12)
                    self.pdf.set_text_color(0, 0, 0)
                    self.pdf.cell(self.content_width, 8, project.strip(), ln=True)
                    y_position += 8

                y_position += 3

        return y_position + 5

    def add_experience(self, experience, y_position):
        """Add experience section"""
        y_position = self.add_section_header("WORK EXPERIENCE", y_position)

        exp_list = experience.split(";")
        for exp in exp_list:
            if exp.strip():
                if self.layout == "sidebar":
                    self.pdf.set_xy(self.content_x, y_position)
                else:
                    self.pdf.set_xy(10, y_position)

                exp_parts = exp.split(":")

                if len(exp_parts) > 1:
                    # Company & position
                    self.pdf.set_font(self.font, "B", 12)
                    self.pdf.set_text_color(0, 0, 0)
                    self.pdf.cell(self.content_width, 8, exp_parts[0].strip(), ln=True)

                    # Experience details
                    y_position += 8
                    if self.layout == "sidebar":
                        self.pdf.set_xy(self.content_x, y_position)
                    else:
                        self.pdf.set_xy(10, y_position)

                    self.pdf.set_font(self.font, "", 11)
                    self.pdf.multi_cell(self.content_width, 6, exp_parts[1].strip())
                    y_position += self.pdf.get_y() - y_position
                else:
                    # Just company name
                    self.pdf.set_font(self.font, "B", 12)
                    self.pdf.set_text_color(0, 0, 0)
                    self.pdf.cell(self.content_width, 8, exp.strip(), ln=True)
                    y_position += 8

                y_position += 3

        return y_position

    def generate_resume(self, form_data, photo_path=None):
        """Generate PDF based on form data and template"""
        # Set up starting position
        y_position = 40

        # Add photo if provided
        has_photo = False
        if photo_path:
            self.add_photo(photo_path)
            has_photo = True

        # Add header with name and contact info
        self.add_header(
            form_data.get("name", ""),
            form_data.get("email", ""),
            form_data.get("phone", ""),
            has_photo=has_photo,
        )

        # Add education section
        y_position = self.add_education(
            form_data.get("degree", ""),
            form_data.get("percentage", ""),
            form_data.get("cgpa", ""),
            form_data.get("college", ""),
            y_position,
        )

        # Add projects section
        y_position = self.add_projects(form_data.get("projects", ""), y_position)

        # Add experience section
        y_position = self.add_experience(form_data.get("experience", ""), y_position)

        # Create BytesIO object to hold the PDF
        pdf_output = self.pdf.output(dest="S").encode(
            "latin1"
        )  # Correct way to get bytes
        pdf_bytes = BytesIO(pdf_output)
        pdf_bytes.seek(0)
        return pdf_bytes


def generate_resume_pdf(form_data, photo_path=None):
    """Factory function to create resume PDF"""
    # Create resume generator with selected template
    resume_gen = CanvaResumeGenerator(form_data["template"])

    # Generate the PDF
    return resume_gen.generate_resume(form_data, photo_path)


@app.route("/")
def index():
    return render_template("index.html", templates=TEMPLATES)


@app.route("/generate_preview", methods=["POST"])
def generate_preview():
    try:
        # Store form data in session
        form_data = {key: request.form[key] for key in request.form}
        session["form_data"] = form_data

        # Handle photo upload
        photo_path = None
        if "photo" in request.files:
            photo = request.files["photo"]
            if photo and allowed_file(photo.filename):
                # Create a unique filename
                filename = secure_filename(photo.filename)
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                unique_filename = f"{timestamp}_{filename}"
                photo_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
                photo.save(photo_path)
                session["photo_path"] = photo_path

        # Generate PDF for preview
        pdf_bytes = generate_resume_pdf(form_data, photo_path)

        # Save PDF temporarily for preview
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        preview_pdf_path = os.path.join(
            app.config["UPLOAD_FOLDER"], f"preview_{timestamp}.pdf"
        )
        with open(preview_pdf_path, "wb") as f:
            f.write(pdf_bytes.read())

        # Store preview path in session
        session["preview_pdf_path"] = preview_pdf_path

        pdf_url = url_for(
            "static", filename=f"uploads/{os.path.basename(preview_pdf_path)}"
        )

        return jsonify({"success": True, "pdf_url": pdf_url})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/preview", methods=["POST"])
def preview_resume():
    # Retrieve form data from session
    form_data = {key: request.form[key] for key in request.form}
    session["form_data"] = form_data
    photo_path = None

    if "photo" in request.files:
        photo = request.files["photo"]
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            unique_filename = f"{timestamp}_{filename}"
            photo_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
            photo.save(photo_path)
            session["photo_path"] = photo_path

    # Generate PDF
    pdf_bytes = generate_resume_pdf(form_data, photo_path)

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    preview_pdf_path = os.path.join(
        app.config["UPLOAD_FOLDER"], f"preview_{timestamp}.pdf"
    )

    with open(preview_pdf_path, "wb") as f:
        f.write(pdf_bytes.read())

    session["preview_pdf_path"] = preview_pdf_path

    template_name = TEMPLATES[form_data["template"]]["name"]

    return render_template(
        "preview.html",
        template_name=template_name,
        preview_pdf_path=url_for(
            "static", filename=f"uploads/{os.path.basename(preview_pdf_path)}"
        ),
    )


@app.route("/generate", methods=["POST"])
def generate_resume():
    form_data = session.get("form_data", {})
    photo_path = session.get("photo_path", None)

    if not form_data:
        return redirect(url_for("index"))

    pdf_bytes = generate_resume_pdf(form_data, photo_path)
    return send_file(
        pdf_bytes,
        as_attachment=True,
        download_name="resume.pdf",
        mimetype="application/pdf",
    )


@app.route("/download")
def download_resume():
    if "preview_pdf_path" in session:
        preview_path = session["preview_pdf_path"]
        return send_file(preview_path, as_attachment=True, download_name="resume.pdf")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
