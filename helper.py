import json

###########################################################################################################
## Here we define some helper functions that will clean up our data and format JSON dicts                ##
###########################################################################################################

def prettify(json_dict): 
    """
    Returns a formatted json to improve readability
    """
    return json.dumps(json_dict, indent=2)

def clean_data(dataframe):
    """ Takes in a dataframe containing covid publication data.
        Removes NaN's, drop irrelevant columns, converts into json format 

    :param dataframe: a Dataframe containing Covid related articles data
    :type dataframe: pd.Dataframe, required
    """
    
    #drop irrelevant information
    dataframe = dataframe.drop(['sha', 'source_x', 'doi', 'pmcid', 'pubmed_id','license','Microsoft Academic Paper ID' , 'WHO #Covidence', 'has_full_text', 'full_text_file','url'], axis=1)
    
    #of the relevant columns drop entries with missing values
    dataframe = dataframe.dropna()
    dataframe = dataframe.reset_index(drop=True)
    
    #convert the authors into a list
    dataframe['authors'] = dataframe.loc[:,'authors'].apply(lambda x: x.split(';'))
    
    #convert the dataframe into JSON for ease of use later with weaviate
    result = dataframe.to_json(orient="records")
    data = json.loads(result)
    
    return data
