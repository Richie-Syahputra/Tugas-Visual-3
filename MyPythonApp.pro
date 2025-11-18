# Tells Qt Creator this is a non-buildable project
TEMPLATE = aux

# List all the Python files you want to appear in the Projects pane
SOURCES += \
    crud_hukum.py \
    dialog_klien.py \
    form_klien_ui.py \
    mainwindow.py \
    ui_form.py
    # Add any other .py files here

# List the .ui files so you can double-click and edit them in Designer
FORMS += \
    form.ui \
    formAnggota.ui
