def split(pdf_file, out_dir=None, naming_fun=None):
    try:
        from pypdf import PdfFileReader, PdfFileWriter
    except ImportError:
        from PyPDF2 import PdfFileReader, PdfFileWriter
    from pathlib import Path
    from tqdm import tqdm
    pdf_file = Path(pdf_file).absolute()
    if not out_dir:
        out_dir = pdf_file.with_suffix("").name
    out_dir = Path(out_dir).absolute()
    out_dir.mkdir(parents=True, exist_ok=True)
    result = []
    with open(pdf_file, "rb") as f:
        pdf = PdfFileReader(f)
        zfill_width = len(str(pdf.getNumPages()))
        if not naming_fun:
            naming_fun = lambda i: f"{str(i).zfill(zfill_width)}.pdf"
        for i in tqdm(range(pdf.getNumPages())):
            writer = PdfFileWriter()
            writer.addPage(pdf.getPage(i))
            out_file = out_dir / naming_fun(i)
            with open(out_file, "wb") as out_f:
                writer.write(out_f)
            result.append(out_file)
    return result
