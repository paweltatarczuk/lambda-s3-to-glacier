# AWS Lambda function - Duplicity S3 to Glacier

## Description

Simple Lambda function that moves all duplicity files from S3 'STANDARD'
storage class to 'GLACIER' storage class.

Files are moved if all constraints are met:

- Bigger than 128KB
- Not ending with `.manifest` or `.manifest.gpg`
- Storage class is 'STANDARD'

## Environment variables

| Name | Description |
|-|-|
| BUCKET_NAME | (Required) Name of the bucket to process |
| TIMEOUT | Function timeout in seconds, defaults to 30 |

## License

MIT
