import os
import random
import re
import sys
import random

DAMPING = 0.85
SAMPLES = 10000

def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    ranks = dict()
    if len(corpus)==0:
        return ranks
    for p in corpus:
        ranks[p]=1.0/len(corpus)*(1-damping_factor)
    if len(corpus[page])==0:
        for p in corpus:
            ranks[p]+=1.0/len(corpus)*damping_factor
    else:
        for p in corpus[page]:
            ranks[p]+=1.0/len(corpus[page])*damping_factor
    return ranks


def sample_pagerank(corpus: dict, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    ranks = dict()
    pos = random.random()*len(corpus)
    page=None
    for p in corpus.keys():
        ranks[p]=0
        if page==None:
            if pos>=1:
                pos-=1
            else:
                page = p

    t_model = transition_model(corpus, page, damping_factor)
    # iterate
    for i in range(n):
        # choose page
        r = random.random()
        t = 0
        for page in t_model:
            if t+t_model[page]>=r:
                break
            else:
                t+=t_model[page]
        # update ranks
        ranks[page]+=1/n
        # next model based on current page
        t_model = transition_model(corpus, page, damping_factor)
    return ranks


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    ranks = dict()
    for page in corpus:
        ranks[page]=1.0/len(corpus)
    changed = True
    i=0
    while changed:
        changed = False
        i+=1
        new_ranks = dict()
        
        for p in corpus:
            new_ranks[p]=(1-damping_factor)/len(corpus)

        for p in corpus:
            if len(corpus[p])==0:
                for pi in corpus:
                    new_ranks[pi]+=damping_factor*ranks[p]/len(corpus)
            else:
                for pi in corpus[p]:
                    new_ranks[pi]+=damping_factor*ranks[p]/len(corpus[p])
        
        for p in corpus:
            if changed:
                break
            if abs(ranks[page]-new_ranks[page])>=.001:
                changed = True
        ranks=new_ranks
    return ranks


if __name__ == "__main__":
    main()

