"""
Pedidos App - Utilidades
"""
import os
import io
from django.conf import settings
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


def generar_barcode(pedido):
    """Genera el código de barras para un pedido."""
    import barcode
    from barcode.writer import ImageWriter
    
    # Crear directorio si no existe
    barcode_dir = settings.MEDIA_ROOT / 'barcodes'
    os.makedirs(barcode_dir, exist_ok=True)
    
    # Generar código
    codigo = pedido.numero_orden
    barcode_class = barcode.get_barcode_class('code128')
    barcode_instance = barcode_class(codigo, writer=ImageWriter())
    
    # Guardar
    ruta = barcode_dir / codigo
    barcode_instance.save(str(ruta))
    
    return f'barcodes/{codigo}.png'


def crear_pdf_pedido(pedido):
    """Crea un PDF completo del pedido."""
    # Configuración del PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15*mm,
        leftMargin=15*mm,
        topMargin=15*mm,
        bottomMargin=15*mm
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        'Titulo',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=10*mm
    )
    subtitulo_style = ParagraphStyle(
        'Subtitulo',
        parent=styles['Heading2'],
        fontSize=12,
        alignment=TA_LEFT,
        spaceAfter=5*mm
    )
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_LEFT
    )
    negrita_style = ParagraphStyle(
        'Negrita',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica-Bold'
    )
    centrado_style = ParagraphStyle(
        'Centrado',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_CENTER
    )
    
    elementos = []
    
    # Encabezado
    elementos.append(Paragraph(f"PEDIDO #{pedido.numero_orden}", titulo_style))
    elementos.append(Paragraph(f"Estado: {pedido.get_estado_display()}", centrado_style))
    elementos.append(Spacer(1, 10*mm))
    
    # Datos de la óptica
    elementos.append(Paragraph("DATOS DE LA ÓPTICA", subtitulo_style))
    elementos.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceAfter=5*mm))
    
    datos_optica = [
        ['Nombre:', pedido.nombre_optica, 'Fecha:', pedido.fecha_creacion.strftime('%d/%m/%Y')],
        ['Ciudad:', pedido.ciudad_optica, 'RUC:', pedido.ruc_optica],
        ['Vendedor:', pedido.vendedor_optica, 'Teléfono:', pedido.telefono_optica],
    ]
    
    t = Table(datos_optica, colWidths=[40*mm, 55*mm, 30*mm, 55*mm])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
    ]))
    elementos.append(t)
    elementos.append(Spacer(1, 10*mm))
    
    # Tipo de lente
    if pedido.tipo_lente:
        elementos.append(Paragraph("TIPO DE LENTE", subtitulo_style))
        elementos.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceAfter=5*mm))
        lente_data = [
            ['Tipo de Lente:', pedido.get_tipo_lente_display() if pedido.tipo_lente else '-'],
            ['Diseño:', pedido.diseno_lente or '-'],
        ]
        t = Table(lente_data, colWidths=[50*mm, 130*mm])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elementos.append(t)
        elementos.append(Spacer(1, 10*mm))
    
    # Receta
    elementos.append(Paragraph("RECETA", subtitulo_style))
    elementos.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceAfter=5*mm))
    
    # Tabla de receta
    receta_headers = ['Medida', 'O.D.', 'O.I.']
    receta_data = [
        receta_headers,
        ['Esfera', pedido.od_esfera or '-', pedido.oi_esfera or '-'],
        ['Cilindro', pedido.od_cilindro or '-', pedido.oi_cilindro or '-'],
        ['Eje', pedido.od_eje or '-', pedido.oi_eje or '-'],
        ['DNP', pedido.od_dnp or '-', pedido.oi_dnp or '-'],
        ['Altura', pedido.od_altura or '-', pedido.oi_altura or '-'],
        ['Adición', pedido.od_adicion or '-', pedido.oi_adicion or '-'],
    ]
    
    t = Table(receta_data, colWidths=[40*mm, 50*mm, 50*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    elementos.append(t)
    elementos.append(Spacer(1, 10*mm))
    
    # Extras
    if any([pedido.horizontal, pedido.vertical, pedido.puente, pedido.distancia_mecanica]):
        elementos.append(Paragraph("MEDIDAS ADICIONALES", subtitulo_style))
        elementos.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceAfter=5*mm))
        
        extras_data = [
            ['Horizontal:', pedido.horizontal or '-', 'Vertical:', pedido.vertical or '-'],
            ['Puente:', pedido.puente or '-', 'Dist. Mecánica:', pedido.distancia_mecanica or '-'],
        ]
        t = Table(extras_data, colWidths=[40*mm, 50*mm, 40*mm, 50*mm])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        elementos.append(t)
        elementos.append(Spacer(1, 10*mm))
    
    # Montura
    if pedido.montura_descripcion:
        elementos.append(Paragraph("MONTURA", subtitulo_style))
        elementos.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceAfter=5*mm))
        
        montura_data = [
            ['Descripción:', pedido.montura_descripcion],
            ['Estado:', pedido.get_montura_estado_display() if pedido.montura_estado else '-'],
        ]
        t = Table(montura_data, colWidths=[50*mm, 130*mm])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        elementos.append(t)
        
        if pedido.montura_foto:
            try:
                img_path = settings.MEDIA_ROOT / pedido.montura_foto.name
                if os.path.exists(img_path):
                    img = Image(img_path, width=50*mm, height=40*mm)
                    elementos.append(img)
            except:
                pass
        
        elementos.append(Spacer(1, 10*mm))
    
    # Bisel
    if pedido.tipo_bisel:
        elementos.append(Paragraph("BISEL", subtitulo_style))
        elementos.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceAfter=5*mm))
        elementos.append(Paragraph(f"Tipo de Bisel: {pedido.get_tipo_bisel_display()}", normal_style))
        elementos.append(Spacer(1, 10*mm))
    
    # Observaciones
    if pedido.observaciones:
        elementos.append(Paragraph("OBSERVACIONES", subtitulo_style))
        elementos.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceAfter=5*mm))
        elementos.append(Paragraph(pedido.observaciones, normal_style))
        elementos.append(Spacer(1, 10*mm))
    
    # Código de barras
    elementos.append(Spacer(1, 15*mm))
    elementos.append(Paragraph("CÓDIGO DE BARRAS", subtitulo_style))
    elementos.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceAfter=5*mm))
    
    if pedido.barcode:
        try:
            barcode_path = settings.MEDIA_ROOT / pedido.barcode.name
            if os.path.exists(barcode_path):
                img = Image(barcode_path, width=80*mm, height=25*mm)
                elementos.append(img)
        except:
            elementos.append(Paragraph(f"Código: {pedido.numero_orden}", centrado_style))
    
    elementos.append(Paragraph(f"Número de Orden: {pedido.numero_orden}", centrado_style))
    
    # Construir PDF
    doc.build(elementos)
    
    # Devolver respuesta
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="pedido_{pedido.numero_orden}.pdf"'
    
    return response


def generar_barcode_pdf(pedido):
    """Genera un PDF solo con el código de barras."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    styles = getSampleStyleSheet()
    centered_style = ParagraphStyle(
        'Centered',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_CENTER
    )
    
    elementos = []
    
    if pedido.barcode:
        try:
            barcode_path = settings.MEDIA_ROOT / pedido.barcode.name
            if os.path.exists(barcode_path):
                img = Image(barcode_path, width=100*mm, height=30*mm)
                elementos.append(img)
        except:
            pass
    
    elementos.append(Spacer(1, 10*mm))
    elementos.append(Paragraph(f"Pedido: {pedido.numero_orden}", centered_style))
    
    doc.build(elementos)
    
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="barcode_{pedido.numero_orden}.pdf"'
    
    return response