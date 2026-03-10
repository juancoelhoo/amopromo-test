from datetime import datetime
from amo.models import Airport

def get_flight_validation_cases(view_instance, origin_obj: 'Airport', dest_obj: 'Airport'):
    """
    Returns a list of validation rules for flight searching.
    view_instance: refers to 'self' from the APIView to access request params.
    """
    v = view_instance
    
    return [
        {
            "condition": not v.origin_airport or not v.destination_airport,
            "error": "There must be the origin and the destination airports."
        },
        {
            "condition": v.origin_airport == v.destination_airport,
            "error": "The origin and the destination airports must be different."
        },
        {
            "condition": not v.departure_date,
            "error": "There must be the departure date."
        },
        {
            "condition": (datetime.strptime(v.departure_date, '%Y-%m-%d').replace(hour=23, minute=59) < datetime.today()) if v.departure_date else False,
            "error": "The departure date must not be before today."
        },
        {
            "condition": (datetime.strptime(v.return_date, '%Y-%m-%d').replace(hour=23, minute=59) < datetime.strptime(v.departure_date, '%Y-%m-%d')) if v.return_date and v.departure_date else False,
            "error": "The return date must be after the departure date."
        },
        {
            "condition": origin_obj is None,
            "error": "The origin airport is not registered on our database. Please, contact us to check it out."
        },
        {
            "condition": dest_obj is None,
            "error": "The destination airport is not registered on our database. Please, contact us to check it out."
        },
    ]