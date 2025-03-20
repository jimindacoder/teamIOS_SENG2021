from DespatchAdviceFactory import DespatchAdvice
from pydanticModels import models2, models, shipmentModel
from datetime import datetime
from pydantic import ValidationError
import json

# create despatch advice with standard inputs 
def test_create_despatch_advice() -> None:
    factory = DespatchAdvice()
    # import the sample input from the json file
    with open("input.json", "r") as file:
        data = json.load(file)
        
    order_data = data.get("Order")
    shipment_data = data.get("cac:Shipment")

    # validate the fields using the pydantic models
    order = models2.Order(**order_data)
    shipment = shipmentModel.CacShipment(**shipment_data)
    
    # returns a pydantic model of the despatch advice
    advice = factory.create_despatch_advice(order, shipment)

    assert isinstance(advice, models.DespatchAdvice)

# despatch advice when one field is missing. eg shipment or order document 
def test_input_not_complete() -> None:
    with open("input1.json", "r") as file:
        data = json.load(file)
        
    order_data = data.get("Order")
    shipment_data = data.get("cac:Shipment")

    if shipment_data is None:
        assert ({"error": "Shipment details have no been provided"})

    if order_data is None:
        assert ({"error": "Order details have no been provided"})


# despatch advice when the input json has missing fields within it
def test_type_error() -> None:
    # import the sample input from the json file
    with open("input2.json", "r") as file:
        data = json.load(file)
        
    order_data = data.get("Order")
    shipment_data = data.get("cac:Shipment")

    # validate the fields using the pydantic models
    try:
        order = models2.Order(**order_data)
        shipment = shipmentModel.CacShipment(**shipment_data)
    except ValidationError as e:
        assert print(f"There are missing fields within your Order or Shipment json: {e}")

#despatch advice expiry date on lot is 10 years from despatch issue date
def test_automate_expiry_date() -> None:
    factory = DespatchAdvice()
    # import the sample input from the json file
    with open("input.json", "r") as file:
        data = json.load(file)
        
    order_data = data.get("Order")
    shipment_data = data.get("cac:Shipment")

    # validate the fields using the pydantic models
    order = models2.Order(**order_data)
    shipment = shipmentModel.CacShipment(**shipment_data)
    
    # returns a pydantic model of the despatch advice
    advice = factory.create_despatch_advice(order, shipment)
    issue_date = advice.cbc_IssueDate
    issue_date_obj = datetime.strptime(issue_date,'%Y-%m-%d')
    lot_expiry_date = advice.cac_DespatchLine.cac_Item.cac_ItemInstance.cac_LotIdentification.cbc_ExpiryDate

    exp_result = datetime(
            year=issue_date_obj.year + 10,
            month=issue_date_obj.month,
            day=issue_date_obj.day,
        )

    assert lot_expiry_date==exp_result.strftime('%Y-%m-%d')
   
#despatch advice when requested delivery period is not specified, start time is date of issue and end time is 3 days from that
def test_automate_requested_delivery_period() -> None:
    factory = DespatchAdvice()
    # import the sample input from the json file
    with open("input3.json", "r") as file:
        data = json.load(file)
        
    order_data = data.get("Order")
    shipment_data = data.get("cac:Shipment")

    # validate the fields using the pydantic models
    order = models2.Order(**order_data)
    shipment = shipmentModel.CacShipment(**shipment_data)
    
    # returns a pydantic model of the despatch advice
    advice = factory.create_despatch_advice(order, shipment)
    issue_date = advice.cbc_IssueDate
    issue_date_obj = datetime.strptime(issue_date,'%Y-%m-%d')

    expected_delivery = datetime(
        year=issue_date_obj.year,
        month=issue_date_obj.month,
        day=issue_date_obj.day + 3,
    )

    time = datetime.today()
    # Automated requested delivery period
    expcted_period = models.CacRequestedDeliveryPeriod(
        cbc_StartDate=issue_date,
        cbc_StartTime=f"{time.strftime('%H:%M:%S')}",
        cbc_EndDate=f"{expected_delivery.strftime('%Y-%m-%d')}",
        cbc_EndTime=f"{time.strftime('%H:%M:%S')}"
    )

    assert expcted_period==advice.cac_Shipment.cac_Delivery.cac_RequestedDeliveryPeriod