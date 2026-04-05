import sys
import os
import glob
from rank_bm25 import BM25Okapi

WIKI_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'wiki')

def query_wiki(keyword):
    print(f"Applying BM25 semantic query for '{keyword}'...")
    pages = glob.glob(os.path.join(WIKI_DIR, '**', '*.md'), recursive=True)
    pages = [p for p in pages if os.path.basename(p) not in ('index.md', 'log.md')]
    
    corpus_texts = []
    file_map = []
    
    for page in pages:
        with open(page, 'r', encoding='utf-8') as f:
            content = f.read()
            # Tokenize basically by splitting text and lowercasing
            tokenized = content.lower().split()
            corpus_texts.append(tokenized)
            file_map.append(page)
            
    if not corpus_texts:
        print("No knowledge pages exist to search.")
        return []

    bm25 = BM25Okapi(corpus_texts)
    tokenized_query = keyword.lower().split()
    scores = bm25.get_scores(tokenized_query)
    
    # Pack up non-zero scores
    results = [(file_map[i], score) for i, score in enumerate(scores) if score > 0]
    results.sort(key=lambda x: x[1], reverse=True)
    
    top_matches = []
    if results:
        print("Found top matches:")
        for r in results[:5]:  # show top 5
            rel_path = os.path.relpath(r[0], WIKI_DIR)
            print(f"- {rel_path} (Score: {r[1]:.2f})")
            top_matches.append({"path": rel_path, "score": float(r[1])})
    else:
        print("No semantic matches found.")
    
    return top_matches

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python query.py [search_term]")
        sys.exit(1)
    query_wiki(" ".join(sys.argv[1:]))
