from sentence_transformers import SentenceTransformer, util

def compare(str1:str, str2: str, treshold: float = 0.8):    
    sentences = [str1, str2]

    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    #Compute embedding for both lists
    embedding_1= model.encode(sentences[0], convert_to_tensor=True)
    embedding_2 = model.encode(sentences[1], convert_to_tensor=True)

    # Compute the cosine similarity
    similarity_tensor = util.pytorch_cos_sim(embedding_1, embedding_2)

    # Extract the scalar value from the tensor
    similarity_value = similarity_tensor.item()

    if similarity_value > treshold:
        return True
    return False

def find_similiar_sentences(transcription):
    similar_results_ts = []
    for idx, sentence in enumerate(transcription):
        if idx > 0:
            current = sentence['text'] 
            last = transcription[idx-1]['text'] 
            if compare(current, last):
                similar_results_ts.append({
                    "start": sentence["start"],
                    "end": sentence["end"],
                    "compared": current,
                    "compared_to": last 
                })
    return similar_results_ts
