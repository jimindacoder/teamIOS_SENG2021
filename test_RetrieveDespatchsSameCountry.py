import pytest
from unittest.mock import patch, Mock

from retrieveDespatchesSameCountry import lambda_handler

TABLE_NAME = "DespatchAdviceTable"

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

    mock_table.scan.return_value = {
        "Items": [
            {"ID": "1", "ShipmentCountry": "Australia"},
            {"ID": "2", "ShipmentCountry": "Australia"}
        ]
    }

    event = {"queryStringParameters": {"country": "Australia"}}
    response = lambda_handler(event, {})

    assert response["statusCode"] == 200
    assert "despatchAdvices with same ShipmentCountry" in response
    assert response["despatchAdvices with same ShipmentCountry"]["despatchAdvicesIDs"] == ["ID: 1", "ID: 2"]
    mock_table.scan.assert_called_once()

@patch("boto3.resource")
def test_invalid_country(mock_boto_resource, mock_dynamodb):
    mock_resource, mock_table = mock_dynamodb
    mock_boto_resource.return_value = mock_resource

    mock_table.scan.return_value = {
        "Items": []
    }

    event = {"queryStringParameters": {"country": "notacountry"}}
    response = lambda_handler(event, {})

    assert response["statusCode"] == 404
    mock_table.scan.assert_called_once()

@patch("boto3.resource")
def test_empty_parameters(mock_boto_resource, mock_dynamodb):
    mock_resource, mock_table = mock_dynamodb
    mock_boto_resource.return_value = mock_resource

    mock_table.get_item.return_value = {}

    event = {"queryStringParameters": {}}
    response = lambda_handler(event, {})

    assert response["statusCode"] == 400
    mock_table.scan.assert_not_called()