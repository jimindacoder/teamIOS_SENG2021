import pytest
from unittest.mock import patch, Mock

from retrieveAllItemsDespatch import lambda_handler

TABLE_NAME = "DespatchAdviceTable"

# will run before each test function
@pytest.fixture
def mock_dynamodb():
    mock_resource = Mock()
    mock_table = Mock()
    mock_resource.Table.return_value = mock_table

    return mock_resource, mock_table


@patch("boto3.resource")
def test_retrieve_success(mock_boto_resource, mock_dynamodb):
    mock_resource, mock_table = mock_dynamodb
    mock_boto_resource.return_value = mock_resource

    mock_table.get_item.return_value = {
        "Item": {
            "ID": "123",
            "Items": "xml"
        }
    }

    event = {"pathParameters": {"despatchId": "123"}}
    response = lambda_handler(event, {})

    assert response["statusCode"] == 200
    assert response["Items"] == "xml"
    mock_table.get_item.assert_called_once_with(Key={"ID": "123"})

@patch("boto3.resource")
def test_invalid_Id(mock_boto_resource, mock_dynamodb):
    mock_resource, mock_table = mock_dynamodb
    mock_boto_resource.return_value = mock_resource

    mock_table.get_item.return_value = {}

    event = {"pathParameters": {"despatchId": "notexist"}}
    response = lambda_handler(event, {})

    assert response["statusCode"] == 404
    mock_table.get_item.assert_called_once_with(Key={"ID": "notexist"})
    mock_table.delete_item.assert_not_called()