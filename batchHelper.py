from weaviate.batch import Batch
from weaviate.util import generate_uuid5


###########################################################################################################
## Here we define some functions that will help us batch and add data objects and references to weavaite.##
###########################################################################################################

def add_publication(batch: Batch, data: dict) -> str:
    """ Takes in a dataframe containing covid publication data and adds the corresponding 
        object to the weaviate Batch.

    :param batch: a Batch object to which the objects and references will be added
    :type batch: weaviate.client.Batch, required
    :param data: Covid publication data returned from the clean_data function
    :type data: dict, required
    """
    #Define the publication object
    publication_object = {
        'title':data['title'],
        'abstract': data['abstract'],
    }
    #generate a UUID for the publication
    publication_id = generate_uuid5(data['cord_uid'])
    
    # add article to the batch
    batch.add_data_object(
        data_object=publication_object,
        class_name='Publication',
        uuid=publication_id
    )
    
    return publication_id

def add_author(batch: Batch, author_name: str, created_authors: dict) -> str:
    """ Takes in author data and adds the corresponding object to the weaviate Batch.

    :param batch: a Batch object to which the objects and references will be added
    :type batch: weaviate.client.Batch, required
    :param author_name: an author name who has published a covid related publication
    :type author_name: str, required
    :param created_authors: a dictionary keeping track of all author objects and thier UUIDs already created
    :type created_authors: dict, required
    """
    #If author already added to the cluster then return the UUID for author
    if author_name in created_authors:
        return created_authors[author_name]
    
    # generate an UUID for the Author
    author_id = generate_uuid5(author_name)
    
    # add author to the batch
    batch.add_data_object(
        data_object={'name': author_name},
        class_name='Author',
        uuid=author_id
    )
    
    created_authors[author_name] = author_id
    return author_id

def add_journal(batch: Batch, journal: str, created_journals: dict) -> str:
    """ Takes in journal data and adds the corresponding object to the weaviate Batch.

    :param batch: a Batch object to which the objects and references will be added
    :type batch: weaviate.client.Batch, required
    :param journal: a journal in which contains a covid related publication
    :type journal: str, required
    :param created_journals: a dictionary keeping track of all journal objects and thier UUIDs already created
    :type created_journals: dict, required
    """
    #If journal entry already exists, then just return the UUID
    if journal in created_journals:
        return created_journals[journal]
    
    #generate UUID for Journal
    journal_id = generate_uuid5(journal)
    
    #add journal to batch
    batch.add_data_object(
        data_object={'name': journal},
        class_name='Journal',
        uuid=journal_id
    )
    
    created_journals[journal] = journal_id
    return journal_id

def add_author_references(batch: Batch, publication_id: str, author_id: str)-> None:
    """ Takes in publication and author data and adds the corresponding references to the weaviate Batch.

    :param batch: a Batch object to which the objects and references will be added
    :type batch: weaviate.client.Batch, required
    :param publication_id: UUID identifying a publication to connect an author to
    :type publication_id: str, required
    :param author_id: UUID identifying an author of a covid related publication 
    :type author_id: str, required
    """
    
    # add references to the batch
    
    ## Author -> Publication
    batch.add_reference(
        from_object_uuid=author_id,
        from_object_class_name='Author',
        from_property_name='wrotePublication',
        to_object_uuid=publication_id
    )
    
    ## Publication -> Author 
    batch.add_reference(
        from_object_uuid=publication_id,
        from_object_class_name='Publication',
        from_property_name='hasAuthors',
        to_object_uuid=author_id
    )
    
def add_journal_references(batch: Batch, publication_id: str, journal_id: str)-> None:
    """ Takes in publication and journal data and adds the corresponding references to the weaviate Batch.

    :param batch: a Batch object to which the objects and references will be added
    :type batch: weaviate.client.Batch, required
    :param publication_id: UUID identifying a publication to connect an author to
    :type publication_id: str, required
    :param journal_id: UUID identifying a journal that contains a covid related publication 
    :type journal_id: str, required
    """

    ## Journal -> Publication
    batch.add_reference(
        from_object_uuid=journal_id,
        from_object_class_name='Journal',
        from_property_name='hasPublication',
        to_object_uuid=publication_id
    )
    
    ## Publication -> Journal 
    batch.add_reference(
        from_object_uuid=publication_id,
        from_object_class_name='Publication',
        from_property_name='inJournal',
        to_object_uuid=journal_id
    )