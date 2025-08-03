import csv
headers=['agenda_id','record_id','title','start_time','end_time','transcript','summary','embeddings']

with open("add_row.csv", "w", encoding='utf-8') as f_out:
    writer = csv.writer(f_out)
    writer.writerow(headers)
    
    with open("agendas.csv", "r") as f_in:
        reader = csv.reader(f_in)
        
        for row in reader:
            row.append("[]")
            
            writer.writerow(row)