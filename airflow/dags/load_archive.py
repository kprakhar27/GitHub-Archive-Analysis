import os
# import pyarrow.csv as pv
# import pyarrow.parquet as pq
from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
# from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator


from google.cloud import storage

default_args ={
    'owner' : 'airflow'
}

AIRFLOW_HOME = os.environ.get('AIRFLOW_HOME', '/opt/airflow')

URL_PREFIX = 'https://data.gharchive.org/'
URL = URL_PREFIX + '{{ execution_date.strftime(\'%Y-%m-%d-%H\') }}.json.gz'

# URL = "https://data.gharchive.org/{{ execution_date.strftime(\'%Y-%m-%d-%-H\') }}.json.gz"

ZIP_FILE = "{{ execution_date.strftime(\'%Y-%m-%d-%-H\') }}.json.gz"
UNZIP_FILE = "{{ execution_date.strftime(\'%Y-%m-%d-%-H\') }}.json"

# CSV_FILENAME = 'songs.csv'
# PARQUET_FILENAME = CSV_FILENAME.replace('csv', 'parquet')
GCS_PATH = "year_{{ execution_date.strftime(\'%Y\') }}/month_{{ execution_date.strftime(\'%m\') }}/date_{{ execution_date.strftime(\'%d\') }}"
ZIP_OUTFILE = f'{AIRFLOW_HOME}/{ZIP_FILE}'
UNZIP_OUTFILE = f'{AIRFLOW_HOME}/{UNZIP_FILE}'
TABLE_NAME = 'events'

GCP_PROJECT_ID = os.environ.get('GCP_PROJECT_ID')
GCP_GCS_BUCKET = os.environ.get('GCP_GCS_BUCKET')
# BIGQUERY_DATASET = os.environ.get('BIGQUERY_DATASET', 'streamify_stg')


# def convert_to_parquet(csv_file, parquet_file):
#     if not csv_file.endswith('csv'):
#         raise ValueError('The input file is not in csv format')
    
#     # Path(f'{AIRFLOW_HOME}/fhv_tripdata/parquet').mkdir(parents=True, exist_ok=True) 
    
#     table=pv.read_csv(csv_file)
#     pq.write_table(table, parquet_file)


def upload_to_gcs(file_path, bucket_name, blob_name):
    """
    Upload the downloaded file to GCS
    """
    # WORKAROUND to prevent timeout for files > 6 MB on 800 kbps upload speed.
    # (Ref: https://github.com/googleapis/python-storage/issues/74)
    
    # storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    # storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(file_path)


with DAG(
    dag_id = f'load_archive_dag',
    default_args = default_args,
    description = f'Execute only once to create songs table in bigquery',
    schedule_interval="5 * * * *", #At the 5th minute of every hour
    start_date=datetime(2022,3,20),
    catchup=True,
    max_active_runs=3,
    tags=['gharchive']
) as dag:

    download_archive_file_task = BashOperator(
        task_id = "download_archive_file",
        bash_command = f"curl -sSLf {URL} > {ZIP_OUTFILE}"
    )

    unzip_archive_file_task = BashOperator(
        task_id = 'unzip_archive',
        bash_command = f"gzip -d {ZIP_OUTFILE}"
    )

    upload_to_gcs_task = PythonOperator(
        task_id='upload_to_gcs',
        python_callable = upload_to_gcs,
        op_kwargs = {
            'file_path' : UNZIP_OUTFILE,
            'bucket_name' : GCP_GCS_BUCKET,
            'blob_name' : f'{TABLE_NAME}/{GCS_PATH}/{UNZIP_FILE}'
        }
    )

    remove_files_from_local_task=BashOperator(
        task_id='remove_files_from_local',
        bash_command=f'rm {UNZIP_OUTFILE}'
    )

    download_archive_file_task >> unzip_archive_file_task >> upload_to_gcs_task >> remove_files_from_local_task