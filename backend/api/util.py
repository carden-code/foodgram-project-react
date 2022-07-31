import io
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def shopping_cart_pdf(data):
    """
    Метод `shopping_cart_pdf` формирует pdf-файл с перечнем
    и количеством необходимых ингредиентов для рецептов из "Списка покупок".
    """
    buffer = io.BytesIO()
    sh = canvas.Canvas(buffer, pagesize=A4)
    pdfmetrics.registerFont(TTFont('Vela Sans', 'data/Vela Sans.ttf'))
    sh.setFillColorCMYK(0.4, 0, 0.4, 0.2)
    sh.setFont('Vela Sans', 16)
    today = datetime.now()
    sh.drawString(
        220,
        750,
        f'Shopping list {today.strftime("%d")} {today.strftime("%B")}'
    )
    sh.setFont('Vela Sans', 12)
    sh.setFillColorRGB(0, 0, 0)
    textobject = sh.beginText()
    textobject.setTextOrigin(20, 700)
    for number, item in enumerate(data, start=1):
        textobject.textLine(
            f'{number}.  {item["ingredient__name"]} - '
            f'{item["ingredient_total"]}'
            f' {item["ingredient__measurement_unit"]}'
        )
        textobject.moveCursor(0, 2)
    sh.drawText(textobject)
    sh.save()
    buffer.seek(0)
    return buffer
