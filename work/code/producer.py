"""
Created on Fri Oct 29 10:04:48 2021

@author: mockingbird
"""

from kafka import KafkaProducer
from threading import Thread
from json import dumps 
import index_reverse, config, add_file_indexor

class Producer:
    
    def __init__(self):
        config.Config() # import des configurations
        self.indexor = index_reverse.Indexeur_inverse()
        self.server = ['kafka:9093']
        self.topic_index   = "index"
        self.topic_reverse = "reverse_index"
        self.topic_reverse_add_file = "reverse_index_add"
        
        self.producer = KafkaProducer(
                            bootstrap_servers = self.server,
                            value_serializer = lambda x: dumps(x).encode('utf-8-sig'),
                            api_version = (2,0,2))
        
        self.run = True
        self.data_index, self.data_reverse = self.indexor.genereIndexTF()


    def indexProducer(self):
        for doc in self.data_index.items():
            self.producer.send(self.topic_index, value=doc)
            print("sended ok")
        return
    
    
    def reverseProducer(self):
        for doc in self.data_reverse.items():
            self.producer.send(self.topic_reverse, value=doc)
        print("sended ok")
        return
            
    
    def add_file_index(self, data_index_add):
        for doc in data_index_add.items():
            self.producer.send(self.topic_index, value=doc)
            print("sended ok")
        return
            
    
    def add_file_reverse(self, data_reverse_add):
        for doc in data_reverse_add.items():
            self.producer.send(self.topic_reverse_add_file, value=doc)
            print("sended --add ok")
        return
    
    
    def init_addFile(self):
        print("waiting for files...")
        while self.run:
            # creation des threads
            add_file = add_file_indexor.Add_file_indexor()
            data_index_add, data_reverse_add = add_file.reverse_index()
            
            if data_index_add and data_reverse_add:
                index_producer   = Thread(target=self.add_file_index, args=(data_index_add, ))
                reverse_producer = Thread(target=self.add_file_reverse, args=(data_reverse_add, ))
                
                print("Starting index")
                index_producer.start()
                
                print("Starting reverse add")
                reverse_producer.start()
                
                index_producer.join()
                reverse_producer.join()
                print("sending end.")
    
    
    def runProducer(self):
        # creation des threads
        index_producer   = Thread(target=self.indexProducer, args=())
        reverse_producer = Thread(target=self.reverseProducer, args=())

        print("Starting index")
        index_producer.start()
        
        print("Starting reverse")
        reverse_producer.start()
        
        index_producer.join()
        reverse_producer.join()
        print("sending end.")
        
        self.init_addFile()
        
        
    def shutdown(self):
        self.run = False


if __name__ == "__main__":
    # Demarrage du producer envoie des data dans le consumer
    print("indexation...")
    Producer().runProducer()
    