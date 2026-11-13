"""Monta o .zip da entrega de Compliance, QA & Tests (GS 2026/2).

Uso: python montar_entrega.py <pasta_modelo> <pasta_saida>
  <pasta_modelo>: ex. ../build (com GranaAmiga-Arquitetura.archimate e a subpasta archi/
                  contendo visao-00..04.png e visao-00..04.pdf exportados do Archi)
  <pasta_saida>:  ex. ../build/entrega

Passos: (1) regenera o documento com as imagens do Archi, (2) converte para PDF com o
LibreOffice, (3) junta os PDFs das visões num único PDF de diagrama, (4) grava o .txt da
equipe e (5) compacta tudo.
"""
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pymupdf

AQUI = Path(__file__).resolve().parent
SOFFICE = r"C:\Program Files\LibreOffice\program\soffice.exe"
EQUIPE = """Global Solution 2026/2 – CitizenTech · Compliance, Quality Assurance & Tests
Projeto: Grana Amiga – Arquitetura de Soluções (TOGAF + ArchiMate)
Turma: 2TDSPR

RM 567295 – Cassio Ribeiro
RM 567265 – Davi Isac Colin Pereira
RM 568542 – Hugo Souza de Jesus
RM 567300 – Matheus Peres Moraes de Jesus
RM 567651 – Pedro Gonçalves Rodrigues

Conteúdo do .zip:
- GranaAmiga-Documento-Descritivo.pdf / .docx – documento descritivo da solução
- GranaAmiga-Arquitetura.archimate – modelo do Archi (5 visões: completa + uma por camada)
- GranaAmiga-Diagrama-Arquitetura.pdf – visões exportadas do Archi em PDF (vetorial)
"""


def achar(archi: Path, i: int, ext: str):
    """visao-0N.ext ou o nome padrão do Archi: '0N - <nome da visão>.ext'."""
    f = archi / f"visao-0{i}.{ext}"
    if f.exists():
        return f
    return next((g for g in archi.glob(f"0{i} - *.{ext}")), None)


def main(modelo: Path, saida: Path):
    archi = modelo / "archi"
    faltando = [f"visão 0{i} ({ext})" for i in range(5) for ext in ("png", "pdf") if not achar(archi, i, ext)]
    if faltando:
        sys.exit(f"Faltam exportações do Archi em {archi}: {', '.join(faltando)}")
    saida.mkdir(parents=True, exist_ok=True)

    doc = saida / "GranaAmiga-Documento-Descritivo.docx"
    subprocess.run(["node", str(AQUI / "gerar_documento.js"), str(archi), str(doc)], check=True, cwd=AQUI)
    subprocess.run([SOFFICE, "--headless", "--convert-to", "pdf", "--outdir", str(saida), str(doc)],
                   check=True, capture_output=True)

    diagrama = pymupdf.open()
    for i in range(5):
        diagrama.insert_pdf(pymupdf.open(achar(archi, i, "pdf")))
    diagrama.set_metadata({"title": "Grana Amiga – Diagrama de Arquitetura de Soluções (ArchiMate)",
                           "author": "Equipe Grana Amiga – 2TDSPR"})
    diagrama.save(saida / "GranaAmiga-Diagrama-Arquitetura.pdf")

    shutil.copy2(modelo / "GranaAmiga-Arquitetura.archimate", saida / "GranaAmiga-Arquitetura.archimate")
    (saida / "integrantes.txt").write_text(EQUIPE, encoding="utf-8")

    arquivos = ["GranaAmiga-Documento-Descritivo.pdf", "GranaAmiga-Documento-Descritivo.docx",
                "GranaAmiga-Arquitetura.archimate", "GranaAmiga-Diagrama-Arquitetura.pdf", "integrantes.txt"]
    zpath = saida / "GS2026-2_ComplianceQA_GranaAmiga_2TDSPR.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for a in arquivos:
            z.write(saida / a, a)
    # conferência: o zip abre e cada PDF tem páginas
    with zipfile.ZipFile(zpath) as z:
        assert z.testzip() is None
        print("zip ok:", zpath.name, [(i.filename, i.file_size) for i in z.infolist()])
    print("páginas: documento =", pymupdf.open(saida / arquivos[0]).page_count,
          "| diagrama =", pymupdf.open(saida / arquivos[3]).page_count)


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())
