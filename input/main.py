import camelot
from glob import glob

file_list = glob("input/*.pdf")
print(f"Found {len(file_list)} files")
for file in file_list:
    print(f"Processing {file}")
    tables = camelot.read_pdf(
        file,
        flavor="stream",
        row_tol=6,
        edge_tol=500,
        backend="poppler",
        pages="1-end",
        split_text=True,
        strip_text=".\n",
        table_areas=["6,800,584,50"],
        columns=["52,81,113,172,238,278,371,414,455,496,537"],
    )
    for table in tables:
        fig = camelot.plot(table, kind="grid")
        fig.savefig(f"output/page-{table.page}-table-{table.order}.png")
    print(f"Found {len(tables)} tables")
    output_file = file.replace("input", "output").replace(".pdf", ".csv")
    print(f"Writing to {output_file}")
    tables.export(output_file, f="csv", compress=False)
