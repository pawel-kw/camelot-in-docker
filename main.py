import camelot

tables = camelot.read_pdf("test.pdf", lattice=True, backend="poppler", pages="2")
tables.export("test.csv", f="csv", compress=False)
