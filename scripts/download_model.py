""" one-off: downloads bge-m3 into the local cache and prints the two numbers
 (max_seq_length, embedding dim) we hardcoded elsewhere in the project"""

from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-m3")
print(model.max_seq_length)
print(model.get_sentence_embedding_dimension())
