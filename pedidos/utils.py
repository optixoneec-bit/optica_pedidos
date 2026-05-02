"""
Pedidos App - Utilidades
"""
import os
import io
from django.conf import settings
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A5
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


def generar_barcode(pedido):
    """Genera el codigo de barras para un pedido."""
    import barcode
    from barcode.writer import ImageWriter
    
    barcode_dir = settings.MEDIA_ROOT / 'barcodes'
    os.makedirs(barcode_dir, exist_ok=True)
    
    codigo = pedido.numero_orden
    barcode_class = barcode.get_barcode_class('code128')
    barcode_instance = barcode_class(codigo, writer=ImageWriter())
    
    ruta = barcode_dir / codigo
    barcode_instance.save(str(ruta))
    
    return f'barcodes/{codigo}.png'


def crear_pdf_pedido(pedido):
    """Crea un PDF completo del pedido en formato A5 horizontal."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A5),
        rightMargin=5*mm,
        leftMargin=5*mm,
        topMargin=4*mm,
        bottomMargin=4*mm
    )
    
    styles = getSampleStyleSheet()
    subtitulo_style = ParagraphStyle('Subtitulo', parent=styles['Heading2'], fontSize=8, alignment=TA_LEFT, spaceAfter=1*mm)
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=7, alignment=TA_LEFT)
    centered_style = ParagraphStyle('Centered', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER)
    pequena_style = ParagraphStyle('Pequena', parent=styles['Normal'], fontSize=6, alignment=TA_LEFT)
    
    elementos = []
    
    # ===== BARCODE ARRIBA A LA DERECHA =====
    if pedido.barcode:
        try:
            barcode_path = settings.MEDIA_ROOT / pedido.barcode.name
            if os.path.exists(barcode_path):
                # Imagen barcode en una tabla con columna vacia a la izquierda
                # para empujarla a la derecha
                img = Image(barcode_path, width=45*mm, height=14*mm)
                tabla_barcode = [['', img]]
                t_barcode = Table(tabla_barcode, colWidths=[135*mm, 50*mm])
                t_barcode.setStyle(TableStyle([
                    ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                    ('VALIGN', (1, 0), (1, 0), 'TOP'),
                ]))
                elementos.append(t_barcode)
        except:
            pass
    
    elementos.append(Spacer(1, 3*mm))
    
    # ===== DATOS OPTICA, LENTE, MONTURA =====
    col_dato = 28*mm
    
    if pedido.montura_descripcion or pedido.tipo_bisel:
        tabla_datos = [
            [pedido.nombre_optica[:20] or '-', pedido.get_tipo_lente_display()[:12] if pedido.tipo_lente else '-', (pedido.montura_descripcion[:15] or '-')[:15]],
            [f"{pedido.ciudad_optica or '-'} | {pedido.ruc_optica or '-'}", pedido.diseno_lente[:18] or '-', pedido.get_tipo_bisel_display()[:12] if pedido.tipo_bisel else '-'],
        ]
        cols = [col_dato, col_dato, col_dato]
    else:
        tabla_datos = [
            [pedido.nombre_optica[:20] or '-', pedido.get_tipo_lente_display()[:12] if pedido.tipo_lente else '-'],
            [f"{pedido.ciudad_optica or '-'} | {pedido.ruc_optica or '-'}", pedido.diseno_lente[:18] or '-'],
        ]
        cols = [col_dato, col_dato]
    
    t_datos = Table(tabla_datos, colWidths=cols)
    t_datos.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    elementos.append(t_datos)
    elementos.append(Spacer(1, 2*mm))
    
    # ===== RECETA =====
    elementos.append(Paragraph("RECETA", subtitulo_style))
    elementos.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceAfter=1*mm))
    
    # Columnas: Esf, Cil, Eje, DNP, Alt, Adic | Filas: OD, OI
    tabla_receta = [
        ['', 'Esf', 'Cil', 'Eje', 'DNP', 'Alt', 'Adic'],
        ['OD', str(pedido.od_esfera or '-'), str(pedido.od_cilindro or '-'), str(pedido.od_eje or '-'), str(pedido.od_dnp or '-'), str(pedido.od_altura or '-'), str(pedido.od_adicion or '-')],
        ['OI', str(pedido.oi_esfera or '-'), str(pedido.oi_cilindro or '-'), str(pedido.oi_eje or '-'), str(pedido.oi_dnp or '-'), str(pedido.oi_altura or '-'), str(pedido.oi_adicion or '-')],
    ]
    
    col_receta = 16*mm
    t_receta = Table(tabla_receta, colWidths=[col_receta]*7)
    t_receta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
    ]))
    elementos.append(t_receta)
    elementos.append(Spacer(1, 2*mm))
    
    # ===== MEDIDAS + VENDEDOR + OBS =====
    if any([pedido.horizontal, pedido.vertical, pedido.puente, pedido.distancia_mecanica]):
        medidas = f"Med: {pedido.horizontal or '-'} / {pedido.vertical or '-'} / {pedido.puente or '-'} / {pedido.distancia_mecanica or '-'}"
    else:
        medidas = ""
    
    vend_text = f"V: {pedido.vendedor_optica[:10] or '-'} | F: {pedido.fecha_creacion.strftime('%d/%m/%Y')}"
    obs_text = f"OBS: {pedido.observaciones[:40]}" if pedido.observaciones else ""
    
    row = [medidas, vend_text, obs_text]
    widths = [45*mm, 40*mm, 50*mm]
    
    t_fila = Table([row], colWidths=widths)
    t_fila.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 6),
    ]))
    elementos.append(t_fila)
    
    doc.build(elementos)
    
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="pedido_{pedido.numero_orden}.pdf"'
    
    return response


def generar_barcode_pdf(pedido):
    """Genera un PDF solo con el codigo de barras."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A5))
    
    styles = getSampleStyleSheet()
    centered_style = ParagraphStyle('Centered', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER)
    
    elementos = []
    
    if pedido.barcode:
        try:
            barcode_path = settings.MEDIA_ROOT / pedido.barcode.name
            if os.path.exists(barcode_path):
                img = Image(barcode_path, width=70*mm, height=22*mm)
                elementos.append(img)
        except:
            pass
    
    elementos.append(Spacer(1, 5*mm))
    elementos.append(Paragraph(f"Pedido: {pedido.numero_orden}", centered_style))
    
    doc.build(elementos)
    
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="barcode_{pedido.numero_orden}.pdf"'
    
    return response