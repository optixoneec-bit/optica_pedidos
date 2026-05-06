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
        rightMargin=10*mm,
        leftMargin=10*mm,
        topMargin=8*mm,
        bottomMargin=2*mm
    )
    
    styles = getSampleStyleSheet()
    subtitulo_style = ParagraphStyle('Subtitulo', parent=styles['Heading2'], fontSize=11, alignment=TA_LEFT, spaceAfter=0, leading=11)
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=10, alignment=TA_LEFT)
    centered_style = ParagraphStyle('Centered', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER)
    pequena_style = ParagraphStyle('Pequena', parent=styles['Normal'], fontSize=10, alignment=TA_LEFT)
    
    elementos = []
    
    # ===== TITULO ÓPTICA =====
    elementos.append(Paragraph("ÓPTICA", subtitulo_style))
    
    optica_data = [
        ['Óptica:', pedido.nombre_optica[:22] or '-', 'RUC:', pedido.ruc_optica or '-'],
        ['Ciudad:', pedido.ciudad_optica or '-', 'Telf:', pedido.telefono_optica or '-'],
    ]
    t_optica = Table(optica_data, colWidths=[15*mm, 55*mm, 15*mm, 55*mm])
    t_optica.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTSIZE', (1, 0), (1, -1), 10),
        ('FONTSIZE', (3, 0), (3, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'LEFT'),
    ]))
    
    if pedido.barcode:
        try:
            barcode_path = settings.MEDIA_ROOT / pedido.barcode.name
            if os.path.exists(barcode_path):
                img = Image(barcode_path, width=40*mm, height=12*mm)
                # Fila: titulo optica | barcode
                tabla_encabezado = [[t_optica, img]]
                t_encabezado = Table(tabla_encabezado, colWidths=[140*mm, 50*mm])
                t_encabezado.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                    ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                elementos.append(t_encabezado)
        except:
            elementos.append(t_optica)
    else:
        elementos.append(t_optica)
    
    elementos.append(Spacer(1, 0))
    
    # ===== LENTE =====
    elementos.append(Paragraph("LENTE", subtitulo_style))
    
    # ===== DATOS LENTE =====
    tipo_lente = pedido.tipo_lente[:12] if pedido.tipo_lente else '-'
    diseno = pedido.diseno_lente[:18] or '-'
    material = pedido.material[:12] if pedido.material else '-'
    
    tabla_lente = [[tipo_lente, diseno, material]]
    t_lente = Table(tabla_lente, colWidths=[35*mm, 55*mm, 35*mm])
    t_lente.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
    ]))
    elementos.append(t_lente)
    elementos.append(Spacer(1, 0))
    
    # ===== RECETA =====
    elementos.append(Paragraph("RECETA", subtitulo_style))
    elementos.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceAfter=0))
    
    # Columnas: Esf, Cil, Eje, DNP, Alt, Adic | Filas: OD, OI
    tabla_receta = [
        ['', 'Esf', 'Cil', 'Eje', 'DNP', 'Alt', 'Adic'],
        ['OD', str(pedido.od_esfera or '-'), str(pedido.od_cilindro or '-'), str(pedido.od_eje or '-'), str(pedido.od_dnp or '-'), str(pedido.od_altura or '-'), str(pedido.od_adicion or '-')],
        ['OI', str(pedido.oi_esfera or '-'), str(pedido.oi_cilindro or '-'), str(pedido.oi_eje or '-'), str(pedido.oi_dnp or '-'), str(pedido.oi_altura or '-'), str(pedido.oi_adicion or '-')],
    ]
    
    col_receta = 16*mm
    t_receta = Table(tabla_receta, colWidths=[col_receta]*7)
    t_receta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 1), (0, 2), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (0, 1), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
    ]))
    elementos.append(t_receta)
    elementos.append(Spacer(1, 0))
    
    # MONTURA
    montura_text = f"Mont: {pedido.montura_descripcion[:30] or '-'} ({pedido.get_montura_estado_display() if pedido.montura_estado else 'Nueva'})"
    
    # MEDIDAS
    hor = pedido.horizontal or '-'
    vert = pedido.vertical or '-'
    puente = pedido.puente or '-'
    dm = pedido.distancia_mecanica or '-'
    medidas = f"Hor: {hor} | Vert: {vert} | Puente: {puente} | DM: {dm}" if pedido.horizontal else ""
    
    # MONTURA y MEDIDAS titulos en misma fila
    titulo_montura = Paragraph("MONTURA", subtitulo_style)
    titulo_medidas = Paragraph("MEDIDAS", subtitulo_style)
    valor_medidas = Paragraph(medidas, pequena_style)
    
    tabla_montura = [[titulo_montura, titulo_medidas], 
                   [montura_text, valor_medidas]]
    t_montura = Table(tabla_montura, colWidths=[100*mm, 80*mm])
    t_montura.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    elementos.append(t_montura)
    elementos.append(Spacer(1, 0))
    
    # ===== BISEL =====
    elementos.append(Paragraph("BISEL", subtitulo_style))
    bisel_text = pedido.get_tipo_bisel_display() if pedido.tipo_bisel else '-'
    elementos.append(Paragraph(bisel_text, pequena_style))
    elementos.append(Spacer(1, 0))
    
    # ===== TRATAMIENTOS =====
    elementos.append(Paragraph("TRATAMIENTOS", subtitulo_style))
    
    tratamientos = []
    if pedido.tratamiento_fotosensible:
        tratamientos.append(f"<b>Fotosensible:</b> {pedido.tratamiento_fotosensible}")
    if pedido.tratamiento_antireflejo:
        tratamientos.append(f"<b>Antireflejo:</b> {pedido.tratamiento_antireflejo}")
    if pedido.tratamiento_filtro_azul:
        tratamientos.append("<b>Filtro Luz Azul:</b> Sí")
    if pedido.tratamiento_transitions:
        tratamientos.append("<b>Transitions:</b> Sí")
    
    trat_text = " | ".join(tratamientos) if tratamientos else "-"
    elementos.append(Paragraph(trat_text, pequena_style))
    elementos.append(Spacer(1, 0))
    
    # ===== OBSERVACIONES =====
    elementos.append(Paragraph("OBSERVACIONES", subtitulo_style))
    elementos.append(Paragraph(pedido.observaciones[:60] if pedido.observaciones else "-", pequena_style))
    elementos.append(Spacer(1, 0))
    
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