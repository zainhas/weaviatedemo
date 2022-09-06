### import libraries
import streamlit as st
import json
import weaviate

###########################################################################################################
## Create a title.
###########################################################################################################

st.markdown("<h1 style='text-align: center; color: pink;'>COVID-19 Publication Querying Using Weaviate!</h1>", unsafe_allow_html=True)

###########################################################################################################
## Instantiate and connect to the running weaviate cluster:
###########################################################################################################
cluster_name = st.text_input('Enter the Weaviate cluster name that you would like to connect to:')

if len(cluster_name) != 0:
    weaviate_url = 'https://'+cluster_name+'.semi.network'
    client = weaviate.Client(weaviate_url)
    st.write('Connection to Weaviate cluster was sucessful?:',client.is_ready())

###########################################################################################################
## Ask the user for text input to query the database with:
###########################################################################################################
    if client.is_ready():
        text = st.text_input('Enter a topic that you would like to see COVID related academic publications for:')

        if len(text) != 0:
            where_filter = {
                "path": ["abstract"],
                "operator": "Like",
                "valueText": "*"+str(text)+"*"
            }

            query_result = (client.query.get(class_name='Publication', properties=["title","abstract"]).with_where(where_filter).do())
    
            if len(query_result['data']['Get']['Publication']) == 0:
                st.markdown("<h3 style='color: red;'>No articles for that topic were found :( Try another topic!</h3>", unsafe_allow_html=True)
            else:    
                st.markdown("<h3 style='color: green;'>The following publications may interest you:</h3>", unsafe_allow_html=True)

                for paper in query_result['data']['Get']['Publication']:
                    st.write('Title:',paper['title'])
                    with st.expander("Expand for paper details..."):
                        st.write(paper['abstract'])