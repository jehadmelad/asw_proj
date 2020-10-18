import boto3
from numpy import max, min, mean, median


sqs             = boto3.resource('sqs')
s3              = boto3.resource('s3')

# Get the queue
requestQueue    = sqs.get_queue_by_name(QueueName='requestQueue')
responseQueue    = sqs.get_queue_by_name(QueueName='responseQueue')

numbers         = []
# while True:
#     print("waiting requests.............")
# Process messages by printing out body and optional author name
for message in requestQueue.receive_messages():
    rec_list_of_nb = message.body

    # Processing the message from the client
    for nb in rec_list_of_nb.split():
        numbers.append(float(nb))

    print('Sets of numbers received, {}!'.format(numbers))

    # Clacutation phase
    min     = min(numbers)
    max     = max(numbers)
    mean    = mean(numbers)
    median  = median(numbers)
    
    # setting up the reply message
    reply_msg   = """
        Min     = {}   
        Max     = {}   
        Mean    = {}   
        Median  = {}   """.format(min,max,mean,median)
    print(reply_msg)

    # Sending reply message to the queue
    res         = responseQueue.send_message(MessageBody=reply_msg)
    message.delete()

    # generic info used for the bucket
    bkt_name    = "my123-buket9578264"
    file_key    = "log.txt"

    # Creating a bucket if not exist
    s3.create_bucket(
    ACL='private',
    Bucket= bkt_name,
    )

    # saving the transaction info in Log file using S3
    log_file    = open('./log.txt', 'a')
    log_file.write("hello")
    s3.Bucket(bkt_name).upload_file(Filename="log.txt",Key=file_key)
    
    