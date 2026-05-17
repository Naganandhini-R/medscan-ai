# app/tasks/scan_pipeline.py

from app.services.ocr.preprocess import preprocess
from app.services.ocr.detect_logo import detect_logo
from app.services.ocr.compare_layout import compare_layout
from app.services.ocr.scoring import weighted_sum, classify
from app.services.ocr.model import detect_font_anomalies
from app.services.ocr.compare_color import compare_color_histogram

def run_vision_pipeline(image):
    img = preprocess(image)

    logo_score = detect_logo(img)
    layout_score = compare_layout(img)
    color_score = compare_color_histogram(img)
    font_score = detect_font_anomalies(img)

    final_score = weighted_sum(
        logo=logo_score, layout=layout_score, color=color_score, font=font_score
    )

    return {
        "authenticity_score": final_score,
        "status": classify(final_score),
        "signals": {
            "logo": logo_score,
            "layout": layout_score,
            "color": color_score,
            "font": font_score,
        },
    }
