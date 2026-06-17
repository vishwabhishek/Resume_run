import csv
import xlsxwriter

def convert_csv_to_xlsx(csv_file, xlsx_file):
    workbook = xlsxwriter.Workbook(xlsx_file)
    worksheet = workbook.add_worksheet("Top 100 Shortlist")
    
    # Text formatting
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#1A365D',
        'font_color': '#FFFFFF',
        'font_name': 'Calibri',
        'font_size': 11,
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    cell_format = workbook.add_format({
        'font_name': 'Calibri',
        'font_size': 11,
        'valign': 'vcenter',
        'border': 1
    })
    
    score_format = workbook.add_format({
        'font_name': 'Calibri',
        'font_size': 11,
        'num_format': '0.0000',
        'valign': 'vcenter',
        'border': 1
    })
    
    # Read CSV
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
        
    # Write Excel rows
    for r_idx, row in enumerate(rows):
        for c_idx, val in enumerate(row):
            if r_idx == 0:
                worksheet.write(r_idx, c_idx, val, header_format)
            else:
                if c_idx == 1: # rank
                    worksheet.write_number(r_idx, c_idx, int(val), cell_format)
                elif c_idx == 2: # score
                    worksheet.write_number(r_idx, c_idx, float(val), score_format)
                else:
                    worksheet.write(r_idx, c_idx, val, cell_format)
                    
    # Auto-fit columns
    worksheet.set_column(0, 0, 18) # candidate_id
    worksheet.set_column(1, 1, 10) # rank
    worksheet.set_column(2, 2, 12) # score
    worksheet.set_column(3, 3, 90) # reasoning
    
    worksheet.set_row(0, 25) # header height
    for r in range(1, len(rows)):
        worksheet.set_row(r, 20) # data row height
        
    workbook.close()
    print(f"Successfully converted {csv_file} to formatted Excel sheet {xlsx_file}")

if __name__ == "__main__":
    convert_csv_to_xlsx("submission.csv", "submission.xlsx")
