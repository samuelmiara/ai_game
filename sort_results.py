import csv

def sort_and_filter_csv(input_file, output_file, sort_column_index, unique_column_1, unique_column_2, reverse=False):

    with open(input_file, mode='r', newline='') as file:
        reader = csv.reader(file)
        header = next(reader)
        rows = list(reader)


    rows.sort(key=lambda x: x[sort_column_index], reverse=reverse)


    unique_rows = []
    seen_pairs = set()

    for row in rows:
        pair = (row[unique_column_1], row[unique_column_2])
        if pair not in seen_pairs:
            seen_pairs.add(pair)
            unique_rows.append(row)


    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(unique_rows)

    print(f'"{output_file}".')



input_file = "results.csv"
output_file = 'sorted_results.csv'
sort_column_index = 2
unique_column_1 = 0
unique_column_2 = 2
sort_and_filter_csv(input_file, output_file, sort_column_index, unique_column_1, unique_column_2, reverse=True)
