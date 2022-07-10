from django.core.exceptions import BadRequest


def validate_positive_amount(data, value):

    if value < 0:
        error_message = {"message": "Negative Value is unacceptable", "data": data}
        raise BadRequest(error_message)


def check_transfer_not_in_same_account(transfer):

    if transfer["source_account"] == transfer["destination_account"]:
        error_message = {
            "message": "Money Transfer to same account is not possible",
            "data": transfer,
        }
        raise BadRequest(error_message)


def check_account_exist_in_db(request_ids, db_ids):

    for id in request_ids:
        if not db_ids.get(id):
            error_message = {"message": "invalid object", "data": f"id: {id}"}
            raise BadRequest(error_message)

def validate_payload_is_list(payload):
    if not isinstance(payload, dict):

        error_message = {"message": "payload is not a list"}
        raise BadRequest(error_message)
