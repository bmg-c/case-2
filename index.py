def handler(event, context):
    text = event['request']['original_utterance']

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'isBase64Encoded': False,
        'body': 'Hello, {}!'.format(text)
    }
