#!/usr/bin/env python
from gimpfu import *
import os
import sys
import inspect
import locale

# Fix Windows installation failing to import modules from subdirectories in the
# "plug-ins" directory.
#if os.name == "nt":
#  current_module_dirpath = os.path.dirname(inspect.getfile(inspect.currentframe()))
#  if current_module_dirpath not in sys.path:
#    sys.path.append(current_module_dirpath)

# IMPORTING PYTHON MODULES FROM PLUGIN SUBDIRECTORIES
PLUGIN_NAME = "monochromize_pdf"
PLUGINS_DIRPATH = os.path.dirname(inspect.getfile(inspect.currentframe()))
PLUGIN_SUBDIRPATH = os.path.join(PLUGINS_DIRPATH, PLUGIN_NAME)
TRANSLATIONS_DIRPATH = os.path.join(PLUGINS_DIRPATH, PLUGIN_NAME, "translations")

# CONTROLLARE SE FARLO SOLO SU WINDOWS
sys.path.append(PLUGINS_DIRPATH)

# CONTROLLARE SE FARLO SOLO SU WINDOWS
sys.path.append(PLUGIN_SUBDIRPATH)

import i18n
i18n.set('filename_format', '{locale}.{format}')
i18n.set('file_format', 'json') # yaml module not included in python-fu
i18n.load_path.append(TRANSLATIONS_DIRPATH)
# set language
# getdefaultlocale[0] returns one of 'C', 'it_IT', 'en_GB', 'xx_YY', ... or None
language_code = locale.getdefaultlocale()[0];
if (language_code != None):
    i18n.set('locale', language_code)

def monochromize_pdf(input_file, contrast, curves_x):
    #pdb.gimp_message(input_file)
    #pdb.gimp_message(contrast)
    #pdb.gimp_message(curves_x)
    
    # Check input file exists and has pdf extension
    if not os.path.isfile(input_file):
        pdb.gimp_message(i18n.t("The file %s does not exists") % input_file)
        return
    if not input_file.lower().endswith(".pdf"):
        pdb.gimp_message(i18n.t("The file %s does not have pdf extension") % input_file)
        return
    
    ###
    ### CODICE PER APRIRE UN PDF, TRASFORMARLO IN BN 2 COLORI E SALVARLO
    ###
    # DIRETTAMENTE DA PDF
    pdf_input_filename = input_file
    image = pdb.file_pdf_load2(pdf_input_filename, pdf_input_filename, "", 0, [])
    display = None
    #display = pdb.gimp_display_new(image) #decommentare se si vuole vedere il pdf a schermo
    
    # Converto grayscale
    pdb.gimp_image_convert_grayscale(image)
    
    pdb.gimp_image_get_layers(image)
    #(4, (34, 35, 36, 37))
    num_layers = pdb.gimp_image_get_layers(image)[0]
    layers_ids = pdb.gimp_image_get_layers(image)[1]
    max_width = 0
    max_height = 0
    
    for layer_id in layers_ids:
      layer = gimp.Item.from_id(layer_id)
      # Devo ingradire l'immagine, altrimenti vengono usate le dimensioni della prima pagina
      # per tutte le pagine (nel caso le pagine abbiano dimensioni diverse tra loro)
      max_width = max(layer.width, max_width)
      max_height = max(layer.height, max_height)
      
      # Colori - Curve num-points: numero valori x e y = numero punti * 2, control-pts: x1,y1,x2,y2,...
      # almeno due punti 0,0,255,255
      pdb.gimp_curves_spline(layer, HISTOGRAM_VALUE, 6, (0,0,140,0,255,255)) 
      
      # CONTRASTO
      pdb.gimp_brightness_contrast(layer, 0, 20)
    
    # Ridimensiono l'immagine in base alle dimensioni piu' grandi dei vari layer
    image.resize(max_width, max_height)
    
    # Conversione 2 colori b/n
    pdb.gimp_image_convert_indexed(image, NO_DITHER, MONO_PALETTE, 2, False, True, "")  
    
    # Salvataggio file pdf
    pdf_output_filename = pdf_input_filename + "-bn.pdf"
    drawable = pdb.gimp_image_active_drawable(image)
    # flags: ignore-hidden, apply-masks, layers-as-pages, reverse-order
    pdb.file_pdf_save2(image, drawable, pdf_output_filename, pdf_output_filename, False, False, True, True, True)
    
    if display != None:
      pdb.gimp_display_delete(display) #elimina anche l'oggetto image
    else:
      pdb.gimp_image_delete(image)
    
    pdb.gimp_message(i18n.t("Converted file saved in: %s") % pdf_output_filename)

register(
    "python-fu-monochromize-pdf",
    i18n.t("Transform a PDF into a monochrome B/N 2 colors PDF, minimizing size"),
    i18n.t("Transform a PDF into a monochrome B/N 2 colors PDF"),
    "Nicola Inchingolo", "Nicola Inchingolo", "2019",
    i18n.t("Monochromize PDF"),
    "", # type of image it works on (*, RGB, RGB*, RGBA, GRAY etc...)
    [
        (PF_FILE, "input_file", i18n.t("File to convert"), None),
        (PF_SPINNER, "contrast", i18n.t("Contrast"), 20, (0,127,1)),
        (PF_SPINNER, "curves_x", i18n.t("Curves (X)"), 140, (1,254,1))
    ],
    [],
    monochromize_pdf, menu="<Image>/File")  # second item is menu location

main()