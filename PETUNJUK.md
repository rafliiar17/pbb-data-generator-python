# PROJECT_PBB
 generate data 

1. config.json -> berisi config untuk generate data

2. generate_all.py -> berisi script untuk generate data secara otomatis semua

3. generate_keckel.py -> berisi script untuk generate data kecamatan dan kelurahan
                    -> FOLDER/FILE 
                        -> CONFIG_DATA/kecamatan_kelurahan_data.json

4. generate_znt.py -> berisi script untuk generate data znt
                    -> ACTION
                        -> mengambil data dari kecamatan/kelurahan yang aktif dan generate sesuai kelurahan dan kecamatan nya [CONFIG_DATA/kecamatan_kelurahan_data.json]
                    -> FOLDER/FILE
                        -> CONFIG_DATA/znt_data.json

5. generate_kelas.py -> berisi script untuk generate data kelas
                    -> ACTION
                        -> ini hanya menggenerate saja 
                    -> FOLDER/FILE
                        -> CONFIG_DATA/kelas_bumi.json
                        -> CONFIG_DATA/kelas_bangunan.json

6. generate_nop.py -> berisi script untuk generate data nop
                    -> ACTION
                        -> ini mengambil data dari kecamatan/kelurahan yang aktif [CONFIG_DATA/kecamatan_kelurahan_data.json]
                    -> FOLDER/FILE
                        -> PBB_DATA/pbb_generated_nop.json

7. generate_op.py -> berisi script untuk generate data objek pajak
                    -> ACTION
                        -> mengambil data dari kecamatan/kelurahan yang aktif [CONFIG_DATA/kecamatan_kelurahan_data.json]
                        -> mengambil data znt [CONFIG_DATA/znt_data.json]
                        -> mengambil data nop dari hasil generate_nop [PBB_DATA/pbb_generated_nop.json]
                    -> FOLDER/FILE
                        -> PBB_DATA/pbb_data_op_2024.json

8. processing_assesment.py -> berisi script untuk proses penilaian
                    -> ACTION
                        -> mengambil data dari hasil generate_op [PBB_DATA/pbb_data_op_2024.json]
                        -> mengambil data dari hasil generate_kelas [CONFIG_DATA/kelas_bumi.json] [CONFIG_DATA/kelas_bangunan.json]
                    -> FOLDER/FILE
                        -> PBB_DATA/pbb_data_assesment.json
                        -> PBB_DATA_BACKUP/pbb_data_assesment_{TIMESTAMP}.json

9. processing_determination_1.py -> berisi script untuk proses generate data" untuk penetapan
                        -> ACTION
                            -> Menggenerate saja data-data untuk proses penetapan
                        -> FOLDER/FILE
                            -> PBB_DATA_PROCESSING/pbb_data_for_determination.json
                            -> PBB_DATA_PROCESSING_BACKUP/pbb_data_processing_determination_{TIMESTAMP}.json

10. generate_paycode.py -> berisi script untuk generate data paycode
                        -> ACTION
                            -> mengambil data dari hasil proses penetapan [PBB_DATA_PROCESSING/pbb_data_for_determination.json]
                        -> FOLDER/FILE
                            -> PBB_DATA_PROCESSING/pbb_data_paycode.json

11. processing_determination_2.py -> berisi script untuk proses penetapan sebenarnya 
                        -> ACTION
                            -> Mengambil data dari hasil generate_op [PBB_DATA/pbb_data_op_2024.json]
                            -> mengambil data dari hasil assesment [PBB_DATA_PROCESSING/pbb_data_assesment.json]
                            -> Mengambil data dari hasil proses penetapan [PBB_DATA_PROCESSING/pbb_data_processing_determination.json]
                            -> diproses datanya agar disatukan ke 1 file ke folder [PBB_DATA_PENETAPAN]/{TAHUN}/pbb_sppt.json
                        -> FOLDER/FILE
                            -> PBB_DATA_PENETAPAN/{tahun}/pbb_sppt.json
                            -> PBB_DATA_PENETAPAN_BACKUP/{tahun}/pbb_sppt_{TIMESTAMP}.json
