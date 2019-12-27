from core.settings import WKHTMLTOPDF_PATH
import pdfkit

def get_wkhtmltopdf_config():
    return pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)

