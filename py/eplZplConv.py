import sys
import os
from zebrafy import *
import subprocess

DETACHED_PROCESS = 0x00000008

def convertImgToEplZpl(image_path):
    # Ordnernamen aus dem Dateinamen ohne Endung ableiten
    base_name = os.path.splitext(image_path)[0]
    output_folder = base_name
    
    # Ordner erstellen, falls er nicht existiert
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Dateipfade definieren
    pcx_file = os.path.join(output_folder, os.path.basename(base_name) + ".conv.pcx")
    png_file = os.path.join(output_folder, os.path.basename(base_name) + ".conv.png")
    epl_output_file = os.path.join(output_folder, os.path.basename(base_name) + ".edl.txt")
    zpl_output_file = os.path.join(output_folder, os.path.basename(base_name) + ".zpl.txt")

    # Generell (ImageMagick Konvertierung)
    # Nutze f-strings für sauberere Pfadbehandlung
    subprocess.call(f'magick "{image_path}" -monochrome -negate "{pcx_file}"', creationflags=DETACHED_PROCESS)
    subprocess.call(f'magick "{image_path}" -monochrome -negate "{png_file}"', creationflags=DETACHED_PROCESS)

    # EPL Verarbeitung
    counter = 0
    number_counter = 0
    data_string = ""
    
    with open(pcx_file, 'rb') as infile, open(epl_output_file, 'w') as outfile:
        outfile.write("unsigned char <Aendern>[")
        for byte in infile.read():
            counter += 1
            number_counter += 1
            decimal_value = int(byte)
            data_string += str(decimal_value) + ','
            if counter >= 40:
                data_string += "\n"
                counter = 0

        outfile.write(str(number_counter))
        outfile.write("] = { \n")
        outfile.write(data_string)

    # Letztes Komma entfernen und schließen
    with open(epl_output_file, 'r+') as f:
        f.seek(0, 2)
        f.seek(f.tell() - 1, 0)
        f.truncate()
        f.write("};")

    # ZPL Verarbeitung
    with open(png_file, "rb") as img_f:
        zpl_string = ZebrafyImage(img_f.read(), format="Z64", pos_x=10, pos_y=10, invert=True).to_zpl()

    with open(zpl_output_file, "w") as text_file:
        text_file.write(zpl_string)
