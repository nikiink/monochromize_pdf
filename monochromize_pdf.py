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
    
    output_filename = input_file + "-bw.pdf"
    if os.path.isfile(output_filename):
        pdb.gimp_message(i18n.t("The output file %s already exists, delete it and retry") % output_filename)
        return
    
    
    ###
    ### CODE TO OPEN A PDF, TRANSFORM IT IN B/W 2 COLORS AND SAVE IT
    ###
    image = pdb.file_pdf_load2(input_file, input_file, "", 0, [])
    display = None
    #display = pdb.gimp_display_new(image) #decomment to see the pdf opened on screen
    
    # Convert to grayscale
    pdb.gimp_image_convert_grayscale(image)
    
    pdb.gimp_image_get_layers(image)
    #(4, (34, 35, 36, 37))
    num_layers = pdb.gimp_image_get_layers(image)[0]
    layers_ids = pdb.gimp_image_get_layers(image)[1]
    max_width = 0
    max_height = 0
    
    for layer_id in layers_ids:
      layer = gimp.Item.from_id(layer_id)
      # I have to normalize the image, to max width and max height of all pages
      # if pages have different size
      max_width = max(layer.width, max_width)
      max_height = max(layer.height, max_height)
      
      # Colors - Curves num-points: number of x and y values = number of points * 2, control-pts: x1,y1,x2,y2,...
      # at least 2 points 0,0,255,255
      pdb.gimp_curves_spline(layer, HISTOGRAM_VALUE, 6, (0,0,140,0,255,255)) 
      
      # CONTRAST
      pdb.gimp_brightness_contrast(layer, 0, 20)
    
    # Resize image to max width and height between layers
    image.resize(max_width, max_height)
    
    # Convert to 2 colors b/w
    pdb.gimp_image_convert_indexed(image, NO_DITHER, MONO_PALETTE, 2, False, True, "")  
    
    # Now save the converted pdf file
    drawable = pdb.gimp_image_active_drawable(image)
    # flags: ignore-hidden, apply-masks, layers-as-pages, reverse-order
    pdb.file_pdf_save2(image, drawable, output_filename, output_filename, False, False, True, True, False)
    
    if display != None:
      pdb.gimp_display_delete(display) #destroy image object
    else:
      pdb.gimp_image_delete(image)
    
    pdb.gimp_message(i18n.t("Converted file saved in %s") % output_filename)

register(
    "python-fu-monochromize-pdf",
    i18n.t("Transform a PDF into a monochrome B/W 2 colors PDF, minimizing size"),
    i18n.t("Transform a PDF into a monochrome B/W 2 colors PDF"),
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
