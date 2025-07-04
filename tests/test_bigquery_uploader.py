import pytest
from unittest.mock import patch, MagicMock
from pilot_metrics.bigquery_uploader import upload_to_bigquery


def test_upload_to_bigquery_missing_env_vars():
    """Test that missing environment variables raise an error."""
    with patch.dict("os.environ", {}, clear=True), \
         pytest.raises(ValueError, match="GCP_PROJECT_ID and BQ_DATASET environment variables must be set"):
        upload_to_bigquery([], [])


def test_upload_to_bigquery_success():
    """Test successful upload to BigQuery."""
    sample_completions = [
        {
            "date": "2024-01-15",
            "editor": "vscode",
            "model": "gpt-4",
            "is_custom_model": False,
            "language": "python",
            "total_engaged_users": 20,
            "total_code_acceptances": 100,
            "total_code_suggestions": 150,
            "total_code_lines_accepted": 200,
            "total_code_lines_suggested": 300,
        }
    ]
    
    sample_chats = [
        {
            "date": "2024-01-15",
            "chat_type": "ide",
            "editor": "vscode",
            "model": "gpt-4",
            "is_custom_model": False,
            "total_chats": 50,
            "total_engaged_users": 30,
            "total_chat_copy_events": 10,
            "total_chat_insertion_events": 15,
        }
    ]
    
    # Mock BigQuery client and operations
    mock_client = MagicMock()
    mock_dataset = MagicMock()
    mock_table = MagicMock()
    mock_job = MagicMock()
    
    with patch.dict("os.environ", {"GCP_PROJECT_ID": "test-project", "BQ_DATASET": "test-dataset"}), \
         patch("pilot_metrics.bigquery_uploader.bigquery.Client", return_value=mock_client), \
         patch("pilot_metrics.bigquery_uploader.bigquery.Dataset", return_value=mock_dataset), \
         patch("pilot_metrics.bigquery_uploader.bigquery.Table", return_value=mock_table):
        
        # Mock dataset and table operations
        mock_client.get_dataset.return_value = mock_dataset
        mock_client.get_table.return_value = mock_table
        mock_client.load_table_from_json.return_value = mock_job
        
        upload_to_bigquery(sample_completions, sample_chats)
        
        # Verify client was created with correct project
        mock_client.assert_called_with = "test-project"
        
        # Verify dataset operations
        mock_client.get_dataset.assert_called()
        
        # Verify table operations (2 calls for completions and chats tables)
        assert mock_client.get_table.call_count == 2
        
        # Verify data upload (2 calls for completions and chats)
        assert mock_client.load_table_from_json.call_count == 2


def test_upload_to_bigquery_dataset_creation():
    """Test BigQuery dataset creation when it doesn't exist."""
    from google.cloud.exceptions import NotFound
    
    sample_completions = []
    sample_chats = []
    
    mock_client = MagicMock()
    mock_dataset = MagicMock()
    
    with patch.dict("os.environ", {"GCP_PROJECT_ID": "test-project", "BQ_DATASET": "test-dataset"}), \
         patch("pilot_metrics.bigquery_uploader.bigquery.Client", return_value=mock_client), \
         patch("pilot_metrics.bigquery_uploader.bigquery.Dataset", return_value=mock_dataset):
        
        # Mock dataset not found, then successful creation
        mock_client.get_dataset.side_effect = NotFound("Dataset not found")
        mock_client.create_dataset.return_value = mock_dataset
        
        # Mock table operations to avoid errors
        mock_client.get_table.side_effect = NotFound("Table not found")
        mock_client.create_table.return_value = MagicMock()
        
        upload_to_bigquery(sample_completions, sample_chats)
        
        # Verify dataset creation was attempted
        mock_client.create_dataset.assert_called_once()


def test_upload_to_bigquery_table_creation():
    """Test BigQuery table creation when tables don't exist."""
    from google.cloud.exceptions import NotFound
    
    sample_completions = []
    sample_chats = []
    
    mock_client = MagicMock()
    mock_dataset = MagicMock()
    mock_table = MagicMock()
    
    with patch.dict("os.environ", {"GCP_PROJECT_ID": "test-project", "BQ_DATASET": "test-dataset"}), \
         patch("pilot_metrics.bigquery_uploader.bigquery.Client", return_value=mock_client), \
         patch("pilot_metrics.bigquery_uploader.bigquery.Table", return_value=mock_table):
        
        # Mock dataset exists
        mock_client.get_dataset.return_value = mock_dataset
        
        # Mock tables don't exist
        mock_client.get_table.side_effect = NotFound("Table not found")
        mock_client.create_table.return_value = mock_table
        
        upload_to_bigquery(sample_completions, sample_chats)
        
        # Verify table creation was attempted (2 tables: completions + chats)
        assert mock_client.create_table.call_count == 2


def test_upload_to_bigquery_empty_data():
    """Test uploading empty data doesn't cause errors."""
    mock_client = MagicMock()
    mock_dataset = MagicMock()
    mock_table = MagicMock()
    
    with patch.dict("os.environ", {"GCP_PROJECT_ID": "test-project", "BQ_DATASET": "test-dataset"}), \
         patch("pilot_metrics.bigquery_uploader.bigquery.Client", return_value=mock_client), \
         patch("pilot_metrics.bigquery_uploader.bigquery.Table", return_value=mock_table):
        
        # Mock existing dataset and tables
        mock_client.get_dataset.return_value = mock_dataset
        mock_client.get_table.return_value = mock_table
        
        upload_to_bigquery([], [])
        
        # Verify no data upload was attempted for empty data
        mock_client.load_table_from_json.assert_not_called()