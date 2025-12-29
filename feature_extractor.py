
# [DETECTOR / ASSISTANT] - v2 (Chunking Version)
# This script reads the raw JSONL logs, breaks them into small "chunks",
# and creates a numerical feature row for EACH CHUNK.

from curses.ascii import EOT
import pandas as pd
import json
from sklearn.feature_extraction.text import CountVectorizer

def process_log_file_chunked(filepath, label, chunk_size=10):
    """
    Reads a JSONL file and processes it in chunks of 'chunk_size' lines.
    Each chunk is treated as a separate execution trace.
    """
    all_data = []
    
    with open(filepath, 'r') as f:
        # Read all lines from the log file
        lines = f.readlines()
    
    # Process the file in chunks
    for i in range(0, len(lines), chunk_size):
        chunk_lines = lines[i:i + chunk_size]
        
        # Ensure we have a full chunk (or at least some data)
        if not chunk_lines:
            continue
            
        action_sequence = []
        for line in chunk_lines:
            try:
                event = json.loads(line)
                action_sequence.append(event.get('action', 'unknown'))
            except json.JSONDecodeError:
                continue # Skip corrupted log lines
        
        # Join all actions in this chunk into a single space-separated string
        sequence_string = " ".join(action_sequence)
        
        # Add this chunk as a new row of data
        all_data.append({'sequence': sequence_string, 'label': label})
        
    return all_data

def main():
    """ Main function to generate the feature set. """
    print("Starting feature extraction (chunked)...")

    # 1. Load and chunk the data
    all_data_rows = []
    # Process benign logs (label 0)
    all_data_rows.extend(process_log_file_chunked('benign_traces.jsonl', 0, chunk_size=10))
    # Process malicious logs (label 1)
    all_data_rows.extend(process_log_file_chunked('malicious_traces.jsonl', 1, chunk_size=10))
    
    # Convert our list of data into a pandas DataFrame (a table)
    df = pd.DataFrame(all_data_rows)
    
    # 2. Extract Features using CountVectorizer
    print("Vectorizing action sequences...")
    vectorizer = CountVectorizer()
    action_features = vectorizer.fit_transform(df['sequence']).toarray()
    
    # 3. Combine Features
    action_df = pd.DataFrame(action_features, columns=vectorizer.get_feature_names_out())
    final_df = pd.concat([df[['label']], action_df], axis=1)
    
    # 4. Save the Result
    output_path = 'features.csv'
    final_df.to_csv(output_path, index=False)
    
    print(f"Feature extraction complete. Data saved to {output_path}")
    print("\n--- Feature Matrix Preview (first 5 rows) ---")
    print(final_df.head())
    print("\n--- Dataset Shape ---")
    print(f"Total rows (examples): {len(final_df)}")
    print(f"Total columns (features): {len(final_df.columns)}")

if __name__ == '__main__':
    main()
EOT