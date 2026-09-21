from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    
    # Define colors
    blue = RGBColor(0, 80, 160)
    light_blue = RGBColor(230, 240, 255)
    white = RGBColor(255, 255, 255)
    dark_gray = RGBColor(64, 64, 64)

    # 1. Title Slide
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = blue
    
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    
    title.text = "Accessibility Navigation App"
    title.text_frame.paragraphs[0].font.color.rgb = white
    title.text_frame.paragraphs[0].font.bold = True
    
    subtitle.text = "Navigate Without Barriers"
    subtitle.text_frame.paragraphs[0].font.color.rgb = light_blue
    
    # 2. The Problem
    bullet_slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(bullet_slide_layout)
    title = slide.shapes.title
    title.text = "The Problem: Inaccessible Navigation"
    title.text_frame.paragraphs[0].font.color.rgb = blue
    title.text_frame.paragraphs[0].font.bold = True
    
    body_shape = slide.shapes.placeholders[1]
    tf = body_shape.text_frame
    tf.text = "Navigation apps lack accessibility features for wheelchair users and people with disabilities:"
    
    p = tf.add_paragraph()
    p.text = "• Missing ramp information"
    p.level = 1
    p = tf.add_paragraph()
    p.text = "• Unpredictable elevator availability"
    p.level = 1
    p = tf.add_paragraph()
    p.text = "• Hidden stairs on routes"
    p.level = 1
    p = tf.add_paragraph()
    p.text = "• Poor sidewalk conditions (potholes, narrow paths)"
    p.level = 1
    
    # 3. Project Objectives
    slide = prs.slides.add_slide(bullet_slide_layout)
    title = slide.shapes.title
    title.text = "Project Objectives"
    title.text_frame.paragraphs[0].font.color.rgb = blue
    title.text_frame.paragraphs[0].font.bold = True
    
    tf = slide.shapes.placeholders[1].text_frame
    tf.text = "Empower users with disabilities through barrier-free navigation."
    p = tf.add_paragraph()
    p.text = "• Develop an AI-driven routing engine prioritizing accessibility."
    p.level = 1
    p = tf.add_paragraph()
    p.text = "• Provide real-time data on ramps, elevators, and hazards."
    p.level = 1
    p = tf.add_paragraph()
    p.text = "• Generate Accessibility Scores for locations and paths."
    p.level = 1
    p = tf.add_paragraph()
    p.text = "• Build an intuitive, high-contrast, easy-to-use interface."
    p.level = 1

    # 4. Literature Survey
    slide = prs.slides.add_slide(bullet_slide_layout)
    title = slide.shapes.title
    title.text = "Literature Survey"
    title.text_frame.paragraphs[0].font.color.rgb = blue
    title.text_frame.paragraphs[0].font.bold = True
    
    tf = slide.shapes.placeholders[1].text_frame
    tf.text = "Existing solutions fall short on granular accessibility data:"
    p = tf.add_paragraph()
    p.text = "• Traditional Maps: Focus on vehicular & basic pedestrian routing."
    p.level = 1
    p = tf.add_paragraph()
    p.text = "• Wheelmap/AccessMap: Rely on crowdsourced data, often incomplete."
    p.level = 1
    p = tf.add_paragraph()
    p.text = "• Gap: Lack of automated, AI-based surface quality assessment and real-time dynamic routing."
    p.level = 1

    # 5. System Architecture
    slide = prs.slides.add_slide(bullet_slide_layout)
    title = slide.shapes.title
    title.text = "System Architecture"
    title.text_frame.paragraphs[0].font.color.rgb = blue
    title.text_frame.paragraphs[0].font.bold = True
    
    tf = slide.shapes.placeholders[1].text_frame
    tf.text = "A modern, decoupled Microservices Architecture:"
    p = tf.add_paragraph()
    p.text = "• Frontend (React): Responsive PWA for mobile & desktop."
    p.level = 1
    p = tf.add_paragraph()
    p.text = "• Backend (FastAPI): High-performance API routing and AI inference."
    p.level = 1
    p = tf.add_paragraph()
    p.text = "• Mapping Engine (OpenStreetMap): Base map and spatial data."
    p.level = 1
    p = tf.add_paragraph()
    p.text = "• Database (PostgreSQL/PostGIS): Geospatial data storage."
    p.level = 1

    # 6. Dataset Collection
    slide = prs.slides.add_slide(bullet_slide_layout)
    title = slide.shapes.title
    title.text = "Dataset Collection"
    title.text_frame.paragraphs[0].font.color.rgb = blue
    title.text_frame.paragraphs[0].font.bold = True
    
    tf = slide.shapes.placeholders[1].text_frame
    tf.text = "Multi-modal data sourcing for high accuracy:"
    p = tf.add_paragraph()
    p.text = "• OpenStreetMap (OSM) Tags: Extracting wheelchair=yes, incline, surface type."
    p.level = 1
    p = tf.add_paragraph()
    p.text = "• Crowdsourcing: User-reported hazards and elevator outages."
    p.level = 1
    p = tf.add_paragraph()
    p.text = "• Imagery: Street-level images for computer vision training."
    p.level = 1
    p = tf.add_paragraph()
    p.text = "• Government Open Data: City municipal accessibility datasets."
    p.level = 1

    # 7. AI/ML Approach
    slide = prs.slides.add_slide(bullet_slide_layout)
    title = slide.shapes.title
    title.text = "AI/ML Approach"
    title.text_frame.paragraphs[0].font.color.rgb = blue
    title.text_frame.paragraphs[0].font.bold = True
    
    tf = slide.shapes.placeholders[1].text_frame
    tf.text = "Leveraging TensorFlow for spatial analysis:"
    p = tf.add_paragraph()
    p.text = "• Computer Vision: Detecting missing curb ramps and obstacles from street imagery."
    p.level = 1
    p = tf.add_paragraph()
    p.text = "• NLP: Parsing user reviews to extract accessibility insights."
    p.level = 1
    p = tf.add_paragraph()
    p.text = "• Predictive Modeling: Estimating elevator uptime based on historical patterns."
    p.level = 1

    # 8. Route Optimization
    slide = prs.slides.add_slide(bullet_slide_layout)
    title = slide.shapes.title
    title.text = "Route Optimization"
    title.text_frame.paragraphs[0].font.color.rgb = blue
    title.text_frame.paragraphs[0].font.bold = True
    
    tf = slide.shapes.placeholders[1].text_frame
    tf.text = "Custom graph algorithms for safe traversal:"
    p = tf.add_paragraph()
    p.text = "• Avoidance Routing: Penalize stairs, steep inclines (>8%), and rough surfaces."
    p.level = 1
    p = tf.add_paragraph()
    p.text = "• Multi-Objective A* Algorithm: Balance distance vs. accessibility safety."
    p.level = 1
    p = tf.add_paragraph()
    p.text = "• Dynamic Rerouting: Real-time adjustments based on live hazard reports."
    p.level = 1

    # 9. Accessibility Scoring
    slide = prs.slides.add_slide(bullet_slide_layout)
    title = slide.shapes.title
    title.text = "Accessibility Scoring"
    title.text_frame.paragraphs[0].font.color.rgb = blue
    title.text_frame.paragraphs[0].font.bold = True
    
    tf = slide.shapes.placeholders[1].text_frame
    tf.text = "A standardized metric for inclusive urban mobility:"
    p = tf.add_paragraph()
    p.text = "• Path Score (1-100): Based on surface smoothness, width, and incline."
    p.level = 1
    p = tf.add_paragraph()
    p.text = "• Venue Score (A-F): Availability of ramps, automated doors, and accessible restrooms."
    p.level = 1
    p = tf.add_paragraph()
    p.text = "• Visualized as a heat map for users to instantly gauge neighborhood accessibility."
    p.level = 1

    # 10. Technology Stack
    slide = prs.slides.add_slide(bullet_slide_layout)
    title = slide.shapes.title
    title.text = "Technology Stack"
    title.text_frame.paragraphs[0].font.color.rgb = blue
    title.text_frame.paragraphs[0].font.bold = True
    
    tf = slide.shapes.placeholders[1].text_frame
    tf.text = "Built with modern, scalable, and robust technologies:"
    p = tf.add_paragraph()
    p.text = "• Frontend: React.js (accessible UI components)"
    p.level = 1
    p = tf.add_paragraph()
    p.text = "• Backend: Python / FastAPI (high performance async API)"
    p.level = 1
    p = tf.add_paragraph()
    p.text = "• AI/ML: TensorFlow (image processing & predictive analytics)"
    p.level = 1
    p = tf.add_paragraph()
    p.text = "• Data/Mapping: OpenStreetMap & PostgreSQL (PostGIS)"
    p.level = 1

    # 11. Expected Outcomes
    slide = prs.slides.add_slide(bullet_slide_layout)
    title = slide.shapes.title
    title.text = "Expected Outcomes"
    title.text_frame.paragraphs[0].font.color.rgb = blue
    title.text_frame.paragraphs[0].font.bold = True
    
    tf = slide.shapes.placeholders[1].text_frame
    tf.text = "Delivering real-world impact:"
    p = tf.add_paragraph()
    p.text = "• Increased Independence: Safer, reliable navigation for wheelchair users."
    p.level = 1
    p = tf.add_paragraph()
    p.text = "• Data Democratization: A rich, open database of accessibility metrics."
    p.level = 1
    p = tf.add_paragraph()
    p.text = "• Community Engagement: Gamified crowdsourcing for continuous updates."
    p.level = 1

    # 12. Timeline
    slide = prs.slides.add_slide(bullet_slide_layout)
    title = slide.shapes.title
    title.text = "Project Timeline"
    title.text_frame.paragraphs[0].font.color.rgb = blue
    title.text_frame.paragraphs[0].font.bold = True
    
    tf = slide.shapes.placeholders[1].text_frame
    tf.text = "Phased execution plan:"
    p = tf.add_paragraph()
    p.text = "• Month 1: Requirements, literature review, and UI/UX design."
    p.level = 1
    p = tf.add_paragraph()
    p.text = "• Month 2: Data collection (OSM setup) and database schema."
    p.level = 1
    p = tf.add_paragraph()
    p.text = "• Month 3: AI model training and FastAPI routing engine development."
    p.level = 1
    p = tf.add_paragraph()
    p.text = "• Month 4: React frontend integration, testing, and deployment."
    p.level = 1

    # 13. Future Enhancements
    slide = prs.slides.add_slide(bullet_slide_layout)
    title = slide.shapes.title
    title.text = "Future Enhancements"
    title.text_frame.paragraphs[0].font.color.rgb = blue
    title.text_frame.paragraphs[0].font.bold = True
    
    tf = slide.shapes.placeholders[1].text_frame
    tf.text = "Scaling the impact beyond the MVP:"
    p = tf.add_paragraph()
    p.text = "• Voice Navigation Integration (Google Assistant / Siri)."
    p.level = 1
    p = tf.add_paragraph()
    p.text = "• Indoor Navigation for malls and transit hubs."
    p.level = 1
    p = tf.add_paragraph()
    p.text = "• AR (Augmented Reality) wayfinding overlays."
    p.level = 1
    p = tf.add_paragraph()
    p.text = "• IoT Integration with smart city infrastructure."
    p.level = 1
    
    # EDA: Score Distribution
    blank_slide_layout = prs.slide_layouts[5] # Title Only
    slide = prs.slides.add_slide(blank_slide_layout)
    title = slide.shapes.title
    title.text = "EDA: Accessibility Score Distribution"
    title.text_frame.paragraphs[0].font.color.rgb = blue
    title.text_frame.paragraphs[0].font.bold = True
    img_path = r"C:\Users\deebi\.gemini\antigravity\brain\07162d55-931e-4ee9-b7b1-72f37aa1245b\eda_reports\score_distribution.png"
    slide.shapes.add_picture(img_path, Inches(1), Inches(2), width=Inches(8))

    # EDA: Feature Correlation
    slide = prs.slides.add_slide(blank_slide_layout)
    title = slide.shapes.title
    title.text = "EDA: Feature Correlation Heatmap"
    title.text_frame.paragraphs[0].font.color.rgb = blue
    title.text_frame.paragraphs[0].font.bold = True
    img_path = r"C:\Users\deebi\.gemini\antigravity\brain\07162d55-931e-4ee9-b7b1-72f37aa1245b\eda_reports\correlation_heatmap.png"
    slide.shapes.add_picture(img_path, Inches(1.5), Inches(1.5), height=Inches(5.5))

    # EDA: Surface vs Score
    slide = prs.slides.add_slide(blank_slide_layout)
    title = slide.shapes.title
    title.text = "EDA: Accessibility by Surface Type"
    title.text_frame.paragraphs[0].font.color.rgb = blue
    title.text_frame.paragraphs[0].font.bold = True
    img_path = r"C:\Users\deebi\.gemini\antigravity\brain\07162d55-931e-4ee9-b7b1-72f37aa1245b\eda_reports\surface_vs_score.png"
    slide.shapes.add_picture(img_path, Inches(0.5), Inches(2), width=Inches(9))

    # 14. Thank You
    slide = prs.slides.add_slide(title_slide_layout)
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = blue
    
    title = slide.shapes.title
    title.text = "Thank You"
    title.text_frame.paragraphs[0].font.color.rgb = white
    title.text_frame.paragraphs[0].font.bold = True
    
    subtitle = slide.placeholders[1]
    subtitle.text = "Navigate Without Barriers"
    subtitle.text_frame.paragraphs[0].font.color.rgb = light_blue

    prs.save('Accessibility_Navigation_App.pptx')
    print("Presentation created successfully as 'Accessibility_Navigation_App.pptx'")

if __name__ == '__main__':
    create_presentation()
