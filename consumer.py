# -*- coding: utf-8 -*-
"""
Created on Fri Oct 29 10:09:00 2021

@author: mockingbird
"""

from kafka import KafkaConsumer
from threading import Thread
from json import loads
import mongo_config

class Consumer:

    def __init__(self):
        self.server = ['localhost:9092']
        self.topic_index = "index"
        self.topic_reverse = "reverse_index"
        self.topic_reverse_add_file = "reverse_index_add"
        
        self.consumer_index = KafkaConsumer(
                                 self.topic_index,
                                 bootstrap_servers = self.server,
                                 # auto_offset_reset='earliest',
                                 enable_auto_commit=True,
                                 group_id='my-group-index',
                                 value_deserializer=lambda x: loads(x.decode('utf-8-sig')),
                                 api_version=(2,0,2))
        
        self.consumer_reverse = KafkaConsumer(
                                 self.topic_reverse,
                                 bootstrap_servers = self.server,
                                 # auto_offset_reset='earliest',
                                 enable_auto_commit=True,
                                 group_id='my-group-reverse',
                                 value_deserializer=lambda x: loads(x.decode('utf-8-sig')),
                                 api_version=(2,0,2))
        
        self.consu_reverse_add = KafkaConsumer(
                                 self.topic_reverse_add_file,
                                 bootstrap_servers = self.server,
                                 # auto_offset_reset='earliest',
                                 enable_auto_commit=True,
                                 group_id='my-group-reverse_add_file',
                                 value_deserializer=lambda x: loads(x.decode('utf-8-sig')),
                                 api_version=(2,0,2))
        
        self.bdd = mongo_config.Mongo_Config()
        
        
    def save_reverse_index_to_mongo(self, message_value):
        """
        Sauve le dico sous forme d'un fichier  racine doc:freq (freq ou tf selon le dico input)
        """
        line = {'word': message_value[0],'text':[]}
        data = message_value[1]
        for x in data.keys():
            if x != 'df':
                 line["text"].append({"name": x, "tf": data[x]})
            else : 
                line["df"]= data[x]
        return line
            

    def save_index_to_mongo(self, message_value):
        """
        Sauve le dico sous forme d'un fichier  racine doc:freq (freq ou tf selon le dico input)
        """
        line = {'text': message_value[0],'word':[]}
        data = message_value[1]
        for x in data.keys():
            if x != 'df':
                 line["word"].append({"name": x, "w_df": data[x]})
            else : 
                line["df"]= data[x]
        return line
        
    
    def consume_loop_index(self):
        """
        fonction du consumer de l'index permet de formater et de sauver dans mongo
        """
        for message in self.consumer_index:
            data = self.save_index_to_mongo(message.value) # formater les data provenant du producer
            try:
                self.bdd.index_collection.insert_one(data) # inserer dans mongo
            except:
                print("error on insert !")
            
    def consume_loop_reverse(self):
        """
        fonction du consumer du reverse permet de formater et de sauver dans mongo
        """
        for message in self.consumer_reverse:
            print(message.value)
            print("**************")
            data = self.save_reverse_index_to_mongo(message.value) # formater les data provenant du producer
            try:
                self.bdd.reverse_index_collection.insert_one(data) # inserer dans mongo
            except:
                print("error on insert !")
            
    def consume_loop_reverse_update_add(self):
        for message in self.consu_reverse_add:
            data = self.save_reverse_index_to_mongo(message.value) # formater les data provenant du producer
            self.update_bdd_reverse(data) # inserer dans mongo
            print('data reverse add has been recieved')
    
    
    def update_bdd_reverse(self,  dico):
        try:
            for file in dico['text']:
                update = self.bdd.reverse_index_collection.updateMany( 
                    { "word": dico['word'] }, 
                    { "$addToSet": { 
                        "text" : {
                              "name": file['name'], 
                              "tf": file['tf']
                        } 
                    },
                    "df": { '$inc': { 'df': 1 } }
                    })
                if not update:
                    self.bdd.reverse_index_collection.insert_one(dico) # inserer dans mongo
        except:
            print('error on mongo update !')
            
            
    def runConsumer(self):
        """
        lance les thread et initie la procedure [ main() ]
        """
        # Creation des threads 
        index_thread_consumer   = Thread(target = self.consume_loop_index,              args=())
        reverse_thread_consumer = Thread(target = self.consume_loop_reverse,            args=())
        
        add_file_reverse        = Thread(target = self.consume_loop_reverse_update_add, args=())

        # Lancement des threads
        print('waiting for data...')
        index_thread_consumer.start()
        reverse_thread_consumer.start()
        
        add_file_reverse.start()
         
        # attente de tout les threads
        index_thread_consumer.join()
        reverse_thread_consumer.join()
        
        add_file_reverse.join()
    
    
if __name__ == "__main__":
    Consumer().runConsumer()