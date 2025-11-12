from ..scripts.ichorCNA.mark_duplicates_and_insert_sizes_for_TSO500_ichorCNA import compute_insert_size_metrics
from pathlib import Path


bam_file = Path('/staging/tmp/251106_TSO500_Onco/Results/ichorCNA/R73_1-ONC_tumor.bam')
output_dir = Path('/staging/tmp/ichorcna_test')
sample_id = 'R73_1-ONC'

compute_insert_size_metrics(input_bam_path=bam_file, output_directory=output_dir, sample_id=sample_id)

# def compute_insert_size_metrics(input_bam_path: OneOf[str, Path], output_directory: OneOf[str, Path],
#                                 sample_id: str = None) -> subp.Popen:
#     try:
#         picard_path = Path(which('picard'))
#     except TypeError:  # TypeError: expected str, bytes or os.PathLike object, not NoneType
#         raise FileNotFoundError("picard executable not found on system path (looked through the eyes of "
#                                 "shutil.which())")  # re-raise proper exception
#     in_bam_path = Path(input_bam_path)
#     output_dir_path = Path(output_directory)  # this should be on the staging drive!
#     if in_bam_path.parent == output_dir_path:
#         raise ValueError(f"Output directory path must not be identical to input BAM parent directory!")
#     output_dir_path.mkdir(parents=True, exist_ok=True)
#     if sample_id is None:
#         sample_id = in_bam_path.name.split('.markdup.bam')[0]
#     metrics_output_path = output_dir_path / f'{sample_id}-insert_size_metrics.txt'
#     histogram_output_path = output_dir_path / f"{sample_id}-insert_size_histogram.pdf"
#     insert_sizes_tmp_dir = output_dir_path / f'{sample_id}-insert_sizes_tmp_dir'
#     if insert_sizes_tmp_dir.is_dir():
#         rmtree(insert_sizes_tmp_dir, ignore_errors=True)
#     insert_sizes_tmp_dir.mkdir(parents=True, exist_ok=True)
#     # assemble insert size metrices command:
#     insert_sizes_cmd = [str(picard_path), '-Xmx15g',
#                         'CollectInsertSizeMetrics',
#                         f'I="{input_bam_path}"',
#                         f'O="{metrics_output_path}"',
#                         f'H="{histogram_output_path}"',
#                         'M=0.05',
#                         f'TMP_DIR={insert_sizes_tmp_dir}']
#     insert_sizes_proc = subp.Popen(insert_sizes_cmd, encoding='utf-8', stderr=subp.PIPE, stdout=subp.PIPE)
#     return insert_sizes_proc, insert_sizes_tmp_dir