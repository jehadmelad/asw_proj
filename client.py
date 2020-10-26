import boto3
import botocore.exceptions as bx
from sys import argv
import publicip
import logging
import time
import random

logFormat = "%(levelname)s   %(asctime)-15s %(filename)s[%(lineno)d] : %(message)s"
logging.basicConfig(level=logging.INFO,format=logFormat)

logger = logging.getLogger()




author  = ''

class main():
    def __init__(self):
        self.sqs = boto3.resource('sqs')
        logger.info("Starting AWS service SQS....")
        try:
            if not self.sqs.get_queue_by_name(QueueName='requestQueue'):
                self.request_Queue = self.sqs.create_queue(QueueName='requestQueue')
            else:
                print("The request queue is already exist!")
        except bx.ClientError as e:
            logger.debug(e)
            
    
    
    def send_msg(self, msg):
        global author
        author  = str(publicip.get())+str(random.randint(1, 1000))
        request_Queue = self.sqs.get_queue_by_name(QueueName='requestQueue')
        try:
            self.req_smg = request_Queue.send_message(MessageBody=msg, MessageAttributes={'Author': {'StringValue': author,'DataType': 'String' }})
            
            print("Your request has been sent.\n")

        except bx.ClientError:
            print(" here ")
                    
    def receive_msg(self):
        global author
        self.response_Queue = self.sqs.get_queue_by_name(QueueName='responseQueue')
       
        for answer in self.response_Queue.receive_messages(MessageAttributeNames=['Author']):
           
            if answer.message_attributes.get('Author').get('StringValue') == author:
                print("this is      ",author)
                answer_msg = answer.body
                print(answer_msg)
                answer.delete()
                return 1
            else:
        
                print("unable to find the author value....")



if __name__ == "__main__":
    client = main()
    msg = None
    new_msg = ['']
    while msg != "exit":
        msg = input("""
######################################################################\n
Note: sepatated by space for example: 1 5 2.3 9 7.3 \n\
---------------------------------------------------------------\n\
To exist : type <exit>. \n\n
To continue : please Enter your values to be calculated, Note: sepatated by space ? """)
        try:
            if msg != '':
                new_msg = msg.split()
                list(map(float, new_msg))
                if len(new_msg) <= 3:
                    msg = input("\n\
-----------------------------------------------------------------------\n\
You need to enter at least 10 numbers! Press ENTER to try again...!!! ")    
                else:
                    client.send_msg(msg)
                    print("Wait for processing ...")
                    while  client.receive_msg() != 1 :
                        print("waiting a response......")
            else:
                msg = input("\n\
-----------------------------------------------------------------------\n\
Please set your values, example (1 2 3.3 8.2), Press ENTER to try again...!!! ")
        except ValueError:
            if msg != 'exit':
                msg = input("\n\
-----------------------------------------------------------------------\n\
It seems you entred a sring value, Press ENTER to try again...!!!  ")
            else:
                print("\nYou are exiting the application.... ")
                time.sleep(2)
                break

   
    
        



