from pydoc import cli
from createCluster import createCluster
from helper import prettify, clean_data
import json
import pandas as pd
import weaviate 
from weaviate.wcs import WCS
from weaviate.batch import Batch
from weaviate.util import generate_uuid5
import time

#Create cluster or if its already up and running get the URL
weaviate_url = createCluster()

#Connect the client to the weaviate cluster
client = weaviate.Client(weaviate_url)
client.timeout_config = (3, 200)
time.sleep(1)

# empty schema and create new schema
client.schema.get()
client.schema.delete_all()

#Create new schema with Publication, Author and 
schema = {
    "classes": [
        {   #Stores a unique covid related publication with information about title, abstract and references to the journal and authors
            "class": "Publication",
            "description": "A covid related academic publication",
            "properties": [
                {
                    "name": "title",
                    "description": "The title of the publication",
                    "dataType": ["text"]
                }, {
                    "name": "abstract",
                    "description": "The abstract of the publication",
                    "dataType": ["text"]
                }, {
                    #A reference to the authors listed on a publication
                    "name": "hasAuthors",
                    "description": "The authors this publication has",
                    "dataType": ["Author"]
                }, {
                    #A reference to the journal this publication was published in
                    "name": "inJournal",
                    "description": "The journal this was published in",
                    "dataType": ["Journal"]
                }
            ]
        }, {#Stores information about the author and references to publications that author has contributed to
            "class": "Author",
            "description": "An academic author of a covid related publication",
            "properties": [
                {
                "name": "name",
                "dataType": ["string"],
                "description": "The name of the author", 
                },
                {
                #A reference to all the publications the author has written 
                "name": "wrotePublication",
                "dataType": ["Publication"],
                "description": "The publications of the author", 
                }
            ]
        }, {#Stores information about journals and a reference to publications contained therein
            "class": "Journal",
            "description": "An academic journal",
            "properties": [
                {
                "name": "name",
                "dataType": ["string"],
                "description": "The name of the Journal", 
                },
                {
                #A reference to all the publications in this journal
                "name": "hasPublication",
                "dataType": ["Publication"],
                "description": "The publications in the journal", 
                }
            ]
        }
    ]
}

#Create the schema initialized above
client.schema.create(schema)

#To verify that the schema was created correctly uncomment the line below and examine
##print(prettify(client.schema.get()))


#Import CORD dataset
df = pd.read_csv('data/covid_articles.csv')

#clean the data and convert to JSON format
data = clean_data(df)

#Write function to upload dataset to the weaviate cluster

#We will use these dictionaries to make sure the same journal and authors are not upload to weaviate multiple times
#These dictionaries will be modified everytime a new author or journal object is added to the weaviate cluster
created_authors = {}
created_journals = {}


#Below we import some helper functions that will make it easier to upload data to the weaviate cluster in batches
from batchHelper import add_publication, add_author, add_journal, add_author_references, add_journal_references

#Here we define a function that will add our data to weaviate cluster in batches
def add_data(batch: Batch, data: dict, created_authors: dict, created_journals: dict, batch_size=250):
    """Uploads covid publication data to the weaviate cluster in batches.

    :param batch: a Batch object to which the objects and references will be added
    :type batch: weaviate.client.Batch, required
    :param data: covid publications data in JSON dict format
    :type data: JSON dict, required
    :param created_authors: a dictionary keeping track of all author objects and thier UUIDs already created
    :type created_authors: dict, required
    :param created_journals: a dictionary keeping track of all journal objects and thier UUIDs already created
    :type created_journals: dict, required
    :param batch_size: number of data objects to put in one batch, defaults to 250
    :type batch_size: int, optional
    """    

    no_items_in_batch = 0
    batch_no = 1
    #iterate over all the data entries, one row represents one covid publication
    for row in data:

        #Add publication to the batch
        publication_id = add_publication(batch,row)
        
        #Add all authors for this publication to the batch
        for author in row['authors']:
            author_id = add_author(batch, author, created_authors)
            add_author_references(batch, publication_id, author_id)
        
        #Add journal this publication was in to the batch
        journal_id = add_journal(batch, row['journal'], created_journals)
        add_journal_references(batch, publication_id, journal_id)

        
        no_items_in_batch += 1

        #If numbber of objects added exceeds batch side then create the objects in the batch on the cluster
        if no_items_in_batch >= batch_size:
            print('Creating objects and references for batch # ',batch_no,'of',int(len(data)/batch_size))
            batch.create_objects()
            batch.create_references()
            batch_no += 1
            no_items_in_batch = 0

    #Create the remaining objects and references if any left over
    batch.create_objects()
    batch.create_references()
    print('Finished adding data to the weaviate cluster!')
    client.batch.flush()

#To save time we will only add 2500 articles to weaviate rather then all ~34k.
add_data(client.batch, data[:2500], created_authors, created_journals, batch_size=250)


