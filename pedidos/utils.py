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
    
    # ===== DATOS OPTICA MEJORADOS CON TITULOS =====
    # Fila 1: Nombre optica | RUC
    # Fila 2: Ciudad | Telefono
    optica_data = [
        ['Óptica:', pedido.nombre_optica[:22] or '-', 'RUC:', pedido.ruc_optica or '-'],
        ['Ciudad:', pedido.ciudad_optica or '-', 'Telf:', pedido.telefono_optica or '-'],
    ]
    t_optica = Table(optica_data, colWidths=[18*mm, 70*mm, 18*mm, 70*mm])
    t_optica.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('FONTSIZE', (1, 0), (1, -1), 7),
        ('FONTSIZE', (3, 0), (3, -1), 7),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ALIGN', (3, 0), (3, -1), 'LEFT'),
    ]))
    elementos.append(t_optica)
    elementos.append(Spacer(1, 2*mm))
    
    # ===== LENTE =====
    elementos.append(Paragraph("LENTE", subtitulo_style))
    
    # ===== DATOS LENTE =====
    tipo_lente = pedido.get_tipo_lente_display()[:15] if pedido.tipo_lente else '-'
    diseno = pedido.diseno_lente[:20] or '-'
    material = pedido.material[:15] if pedido.material else '-'
    
    tabla_lente = [[tipo_lente, diseno, material]]
    t_lente = Table(tabla_lente, colWidths=[40*mm, 60*mm, 40*mm])
    t_lente.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
    ]))
    elementos.append(t_lente)
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
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 1), (0, 2), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (0, 1), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
    ]))
    elementos.append(t_receta)
    elementos.append(Spacer(1, 2*mm))
    
    # ===== MONTURA =====
    elementos.append(Paragraph("MONTURA", subtitulo_style))
    
    montura_text = f"Mont: {pedido.montura_descripcion[:30] or '-'}"
    estado_text = f"({pedido.get_montura_estado_display() if pedido.montura_estado else 'Nueva'})"
    
    tabla_montura = [[montura_text, estado_text]]
    t_montura = Table(tabla_montura, colWidths=[140*mm, 30*mm])
    t_montura.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 6),
    ]))
    elementos.append(t_montura)
    elementos.append(Spacer(1, 2*mm))
    
    # ===== BISEL =====
    elementos.append(Paragraph("BISEL", subtitulo_style))
    bisel_text = pedido.get_tipo_bisel_display() if pedido.tipo_bisel else '-'
    elementos.append(Paragraph(bisel_text, pequena_style))
    elementos.append(Spacer(1, 2*mm))
    
    # ===== TRATAMIENTOS =====
    elementos.append(Paragraph("TRATAMIENTOS", subtitulo_style))
    
    tratamientos = []
    if pedido.tratamiento_fotosensible:
        tratamientos.append(pedido.tratamiento_fotosensible)
    if pedido.tratamiento_antireflejo:
        tratamientos.append(pedido.tratamiento_antireflejo)
    if pedido.tratamiento_filtro_azul:
        tratamientos.append('Filtro Azul')
    if pedido.tratamiento_transitions:
        tratamientos.append('Transitions')
    
    trat_text = " | ".join(tratamientos) if tratamientos else "-"
    elementos.append(Paragraph(f"Trat: {trat_text}", pequena_style))
    elementos.append(Spacer(1, 1*mm))
    
    # ===== MEDIDAS =====
    hor = pedido.horizontal or '-'
    vert = pedido.vertical or '-'
    puente = pedido.puente or '-'
    dm = pedido.distancia_mecanica or '-'
    
    if pedido.horizontal or pedido.vertical or pedido.puente or pedido.distancia_mecanica:
        elementos.append(Paragraph("MEDIDAS", subtitulo_style))
        medidas = f"Hor: {hor}  Vert: {vert}  Puente: {puente}  DM: {dm}"
        elementos.append(Paragraph(medidas, pequena_style))
        elementos.append(Spacer(1, 1*mm))
    
    # ===== OBSERVACIONES =====
    if pedido.observaciones:
        elementos.append(Paragraph("OBSERVACIONES", subtitulo_style))
        elementos.append(Paragraph(pedido.observaciones, pequena_style))
        elementos.append(Spacer(1, 1*mm))
    
    # ===== VENDEDOR Y FECHA =====
    vend_text = f"V: {pedido.vendedor_optica[:12] or '-'} | F: {pedido.fecha_creacion.strftime('%d/%m/%Y')}"
    elementos.append(Paragraph(vend_text, pequena_style))
    
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