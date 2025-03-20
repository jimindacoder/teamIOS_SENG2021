import pytest
from unittest.mock import patch, Mock

from retrieveAllDespatches import lambda_handler

TABLE_NAME = "DespatchAdviceTable"

# will run before each test function
@pytest.fixture
def mock_dynamodb():
    mock_client = Mock()
    
    mock_client.scan.return_value = {
        "Items": [{"ID": {"N": "1"}}, {"ID": {"N": "2"}}]
    }

    return mock_client

@patch("boto3.client")
def test_retrieve_success(mock_boto_client, mock_dynamodb):
    # test correct response
    mock_boto_client.return_value = mock_dynamodb

    response = lambda_handler({}, {})

    assert response["statusCode"] == 200
    assert response["despatchAdvices"]["despatchAdvicesIDs"] == ["ID: 1", "ID: 2"]

@patch("boto3.client")
def test_retrieve_empty_data(mock_boto_client):
    mock_client = Mock()
    mock_client.scan.return_value = {"Items": []}

    mock_boto_client.return_value = mock_client

    response = lambda_handler({}, {})

    assert response["statusCode"] == 204
    assert response["body"]["message"] == "No despatch advice found"