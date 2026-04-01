import sys
sys.path.append('.')

from retrieval.retriever import DocumentRetriever

# Create retriever
r = DocumentRetriever()

# Test 1 — HR role searching for leave policy
print('\n' + '='*50)
print('TEST 1 — HR employee asking about leave')
print('='*50)
results = r.search_by_role('what is the leave policy?', role='HR', n_results=3)

# Test 2 — Finance role searching for budget
print('\n' + '='*50)
print('TEST 2 — Finance employee asking about budget')
print('='*50)
results = r.search_by_role('how does budget approval work?', role='Finance', n_results=3)

# Test 3 — HR trying to access Finance
print('\n' + '='*50)
print('TEST 3 — HR employee trying to access Finance data')
print('='*50)
results = r.search_by_role('what is the budget process?', role='HR', n_results=3)

print('Results returned:', len(results), '(should only be HR docs)')