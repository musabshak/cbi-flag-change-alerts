from flag_alert import main
import time

def lambda_handler(event, context):
    response = {
        'statusCode': '',
        'body': '',
    }

    try:
        message = main()
        response['statusCode'] = 200
        response['body'] = f'Sent message: {message}'
    except Exception as e:
        response['statusCode'] = 500
        response['body'] = f'{type(e).__name__}. {e}'
    
    print("Response:", response)

    return response