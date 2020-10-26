import boto3
import numpy as np
import os
import time


class main():
   
    def __init__(self):
        
        self.sqs             = boto3.resource('sqs')
        print("Starting AWS service SQS....")
        self.s3              = boto3.resource('s3')
        print("Starting AWS service S3....")
        self.request_Queue    = self.sqs.get_queue_by_name(QueueName='requestQueue')
        self.sqs.create_queue(QueueName='responseQueue')
        
   

    def receive_msg(self):
        # To append the request values as float number
        msg         = []
        mes = ''
        # Iterating within the queue, that consist a requests to Process messages 
        
        
        for message in self.request_Queue.receive_messages(MessageAttributeNames=['Author']):
            author_text = ''
            if message.message_attributes is not None:
                author_name = message.message_attributes.get('Author').get('StringValue')
                if author_name:
                    author_text = author_name
                    print(author_name)
                
            recv_list_of_nb = message.body
            print(recv_list_of_nb)

            # Processing the message from the client by changing it from str to float to do some math calculation.
            for nb in recv_list_of_nb.split():
                msg.append(float(nb))
            print('Sets of numbers received, {}!'.format(msg))
            self.operation(author_text, msg )
            message.delete()
        
        
        
    def operation(self,author, msg):
        '''
        Calculating the values coming from the clients in order to get the result of 
        --------------------------------------------------------------------------
        min     : the minimum value within an array.
        max     : The maximum values.
        mean    : The average of the numbers
        median  : a value separating the higher half from the lower half of a set of numbers.
        '''
        from numpy import max, min, mean, median
        # Clacutation phase for example: minimum number of [2, 8, 9, 3, 7, 6] = 2
        auth = author
        min     = min(msg)
        max     = max(msg)
        mean    = mean(msg)
        median  = median(msg)
        
        # setting up the reply message
        reply_msg   = """Results of these numbers {} :
            Min     = {}   
            Max     = {}   
            Mean    = {}   
            Median  = {}   """.format(msg,min,max,mean,median)
        print(reply_msg)

        self.reply(auth, reply_msg)

    def reply(self,author, message):
        '''
        It has the author name of the receiving message and the content of the message.
        -----------------------------------------------------------------------------
        check if the author exist or not then it sent the results of < Operation() > 
            to the resposeQueue to be retrived by the client.
        ------------
        Parameters
        -------------
        author : str
            generated by the receive_msg()
        message : str
            message coming from the client. 
        
        ------------
        return
        -----------
        send message to the same client who asked for a process.
        push log.txt file to S3 bucket service .
        '''
        author = author
        try:
            response_Queue = self.sqs.get_queue_by_name(QueueName='responseQueue')
        except Exception as e:
            print(e)
        if author:
            # Sending reply message to the queue
            response_Queue.send_message(MessageBody=message,MessageAttributes={'Author': {'StringValue': author,'DataType': 'String' }})
            self.s3_log_file()
        else:
            response_Queue.send_message(MessageBody=message)

    def s3_log_file(self):
        '''
        Log file used to create an history of the transaction and it sstored on the AWS cloud 
            the S3 service. and here we need the name of Bucket and the key of the file.
            The name should be unique.
        

        '''

        # generic info used for the bucket
        bkt_name    = "my123-buket9578ccsd264"
        file_key    = "log.txt"

        # Creating a bucket if not exist
        self.s3.create_bucket(
        ACL='private',
        Bucket= bkt_name,
        )

        # saving the transaction info in Log file using S3
        log_file    = open('./log.txt', 'a')
        log_file.write("\n {}".format("content 1 1 11 1 \n"))
        log_file.close()
        self.s3.Bucket(bkt_name).upload_file(Filename="log.txt",Key=file_key)
        
    

if __name__ == '__main__':
     # Create instances of SQS and S3 bucket
    server = main()
    print(" server running....")
    time.sleep(1)
    while True:
        try:
            print("waiting for the process....")
            server.receive_msg()
            time.sleep(0.2)
        except KeyboardInterrupt:
            print("Process is shutdown, Loading. . . . . ")
            time.sleep(3)
            break
        
