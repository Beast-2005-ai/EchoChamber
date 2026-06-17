import redis
import json
import time
from sentence_transformers import SentenceTransformer

# Load the local model (It will download a small ~80MB model on the first run)
print("Loading Transformer model (all-MiniLM-L6-v2)...")
model = SentenceTransformer('all-MiniLM-L6-v2') 

# Redis Connection Setup
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def process_queue():
    print("Listening for raw news on Redis...")
    while True:
        # BRPOP is a blocking pop: it waits patiently until an item hits the queue
        result = r.brpop('raw_news_queue', timeout=0)
        
        if result:
            queue_name, message = result
            data = json.loads(message)
            
            # We are embedding the title for now
            text_to_analyze = data['title']
            print(f"\n[+] Processing: {text_to_analyze}")
            
            # Generate the Vector Embedding
            embedding = model.encode(text_to_analyze)
            
            print(f"    -> Generated Vector of size: {len(embedding)}")
            
            # Next up: We will pass this embedding to a database to check for mutations!

if __name__ == "__main__":
    try:
        r.ping()
        process_queue()
    except redis.ConnectionError:
        print("Failed to connect to Redis. Is the container running?")
    except KeyboardInterrupt:
        print("\nStopping ML analyzer...")