from pdfminer.high_level import extract_text

text = extract_text('oma format.pdf')
with open('oma_format.txt', 'w', encoding='utf-8') as f:
    f.write(text)
print('Done')