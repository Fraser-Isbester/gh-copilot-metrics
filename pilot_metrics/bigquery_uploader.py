import os
from typing import Any

from google.cloud import bigquery
from google.cloud.exceptions import NotFound


def upload_to_bigquery(
    completions_data: list[dict[str, Any]], chats_data: list[dict[str, Any]]
) -> None:
    """
    Uploads flattened Copilot data to BigQuery tables.

    Requires environment variables:
    - GCP_PROJECT_ID: Google Cloud Project ID
    - BQ_DATASET: BigQuery dataset name
    """
    project_id = os.getenv("GCP_PROJECT_ID")
    dataset_name = os.getenv("BQ_DATASET")

    if not project_id or not dataset_name:
        raise ValueError(
            "GCP_PROJECT_ID and BQ_DATASET environment variables must be set"
        )

    client = bigquery.Client(project=project_id)
    dataset_id = f"{project_id}.{dataset_name}"

    # Ensure dataset exists
    try:
        client.get_dataset(dataset_id)
    except NotFound:
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = "US"
        client.create_dataset(dataset, exists_ok=True)

    # Define table schemas
    completions_schema = [
        bigquery.SchemaField("date", "DATE"),
        bigquery.SchemaField("editor", "STRING"),
        bigquery.SchemaField("model", "STRING"),
        bigquery.SchemaField("is_custom_model", "BOOLEAN"),
        bigquery.SchemaField("language", "STRING"),
        bigquery.SchemaField("total_engaged_users", "INTEGER"),
        bigquery.SchemaField("total_code_acceptances", "INTEGER"),
        bigquery.SchemaField("total_code_suggestions", "INTEGER"),
        bigquery.SchemaField("total_code_lines_accepted", "INTEGER"),
        bigquery.SchemaField("total_code_lines_suggested", "INTEGER"),
    ]

    chats_schema = [
        bigquery.SchemaField("date", "DATE"),
        bigquery.SchemaField("chat_type", "STRING"),
        bigquery.SchemaField("editor", "STRING"),
        bigquery.SchemaField("model", "STRING"),
        bigquery.SchemaField("is_custom_model", "BOOLEAN"),
        bigquery.SchemaField("total_chats", "INTEGER"),
        bigquery.SchemaField("total_engaged_users", "INTEGER"),
        bigquery.SchemaField("total_chat_copy_events", "INTEGER"),
        bigquery.SchemaField("total_chat_insertion_events", "INTEGER"),
    ]

    # Create or update tables
    completions_table_id = f"{dataset_id}.code_completions"
    chats_table_id = f"{dataset_id}.chats"

    completions_table = bigquery.Table(completions_table_id, schema=completions_schema)
    chats_table = bigquery.Table(chats_table_id, schema=chats_schema)

    try:
        client.get_table(completions_table_id)
    except NotFound:
        client.create_table(completions_table)

    try:
        client.get_table(chats_table_id)
    except NotFound:
        client.create_table(chats_table)

    # Upload data
    if completions_data:
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        )

        completions_job = client.load_table_from_json(
            completions_data, completions_table_id, job_config=job_config
        )
        completions_job.result()

    if chats_data:
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        )

        chats_job = client.load_table_from_json(
            chats_data, chats_table_id, job_config=job_config
        )
        chats_job.result()
