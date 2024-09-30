from data import get_data, refresh_data, preprocess_data
# from sidebar import sidebar
# from refactor_form_pemantauan_satu_prodi_fix_formula_tanpa_prediksi import create_pemantauan_form
from refactor_form_pemantauan_semua_prodi import create_pemantauan_form

existing_djm = get_data('djm')
existing_formula = get_data('formula')
create_pemantauan_form(existing_djm=existing_djm, existing_formula=existing_formula)
