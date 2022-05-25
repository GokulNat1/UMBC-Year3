# Author:      Gokul Natarajam
# Section:     11

import random
import hashlib
import argparse

# read_wordlist() Reads a list of possible passwords from a file
# Input:          wordlist_file; A file containing a word on each line
# Output:         wordlist; A list of words read from the wordlist file
def read_wordlist(wordlist_file):
    wordlist = []
    with open(wordlist_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            wordlist.append(line.strip())
    return wordlist


# read_hashes() Reads a list of SHA-256 password hashes from a file
# Input:        hash_file; A file containing a hash on each line
# Output:       hashes; A set of SHA-256 hashes to crack
def read_hashes(hash_file):
    hashes = []
    with open(hash_file, "r") as f:
        for line in f:
            hashes.append(line.strip())
    return hashes


# write_rt() Writes rainbow table to a file
# Input:     rt_file; A file to write the rainbow table to
# Input:     start_words; A list of the first word in each chain
# Input:     end_words; A list of corresponding last words
# Output:    None
def write_rt(rt_file, start_words, end_words):
    with open(rt_file, "w") as f:
        for start_word, end_word in zip(start_words, end_words):
            f.write("{}\t{}\n".format(start_word, end_word))
    return


# read_rt() Reads a rainbow table from a file
# Input:    rt_file; A file containing start/end word of chain on each line
# Output:   chains; A dict of format {start_word: end_word}
def read_rt(chain_file):
    chains = {}
    with open(chain_file, "r") as f:
        for line in f:
            line = line.strip().split("\t")
            if len(line) != 2:
                continue
            start_word, end_word = line[0], line[1]
            chains[start_word] = end_word
    return chains


# H()      The hash function H
# Input:   m; The word to hash
# Output:  h; The hash digest h = H(m) in hex string format
def H(m):
    # Compute SHA-256 hash of m
    hasher = hashlib.sha256()
    hasher.update(m.encode("utf-8"))
    h = hasher.hexdigest()
    return h


# R()      The reduction function Ri
# Input:   h; SHA-256 hash digest
# Input:   i; Position in hash chain
# Output:  m; A word in the wordlist m = Ri(h)
def R(wordlist, h, i):
    # Convert SHA-256 hash digest to an integer
    h_num = int(h, 16)

    # Each position in the hash chain has a unique reduction function
    # Add i (position in chain) to h_num, then map to index in wordlist
    idx = (h_num + i) % len(wordlist)
    m = wordlist[idx]
    return m


# get_end_word() Computes a hash chain of length k, returns end word
# Input:         wordlist; a list of words read from the wordlist file
# Input:         start_word; The word to begin the chain from
# Input:         k; The number of hashes in the chain
# Output:        end_word; The last word in the chain
def get_end_word(wordlist, start_word, k):
    m = start_word
    # Compute h = H(m) and m = Ri(h), k times
    for i in range(k):
        h = H(m)
        m = R(wordlist, h, i)
    end_word = m
    return end_word

def get_word(wordlist, hash, i):
    h = hash
    z = "hi"
    for j in range(i, args.k-1):
        z = R(wordlist, h, j)
        h = H(m)
    end = z
    return end

if __name__ == "__main__":

    # Required command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=["generate", "crack"],
                        help="Choose the mode this program runs in")
    parser.add_argument("--num-chains", type=int, required=True,
                        help="Number of hash chains")
    parser.add_argument("-k", type=int, required=True,
                        help="The max hash chain length")

    # Optional command-line arguments
    parser.add_argument("--wordlist-file", default="rockyou.txt",
                        help="The path to the wordlist file")
    parser.add_argument("--hash-file", default="hashes.txt",
                        help="The file containing SHA-256 password hashes to crack")
    parser.add_argument("--rt-file", default="rainbowtable.txt",
                        help="The path of the rainbow table file")
    args = parser.parse_args()

    # Read the wordlist from the provided file
    wordlist = read_wordlist(args.wordlist_file)
    print("Loaded {} words from {}".format(len(wordlist), args.wordlist_file))

    # Read the list of SHA-256 hashes to crack from the provided file
    hashes = read_hashes(args.hash_file)
    print("Loaded {} SHA-256 hashes from {}".format(len(hashes), args.hash_file))

    # Generate the rainbow table
    if args.mode == "generate":

        # Randomly sample the starting word for each chain from the wordlist
        # Store the chosen starting words in the start_words list
        # Hint: Check out the random.sample() function!
        start_words = []
        start_words = random.sample(wordlist, args.num_chains)
        ##print(start_words)

        # Compute all hash chains, store ending word of each in end_words list
        end_words = []
        for i in range(args.num_chains):
            end_words.append(get_end_word(wordlist, start_words[i], args.k))


        # Write hash chains to rainbow table file
        write_rt(args.rt_file, start_words, end_words)
        print("Wrote {} chains to {}".format(len(start_words), args.rt_file))


    # Crack SHA-256 hashes using a rainbow table
    elif args.mode == "crack":

        # Load rainbow table into chains dict of format {start_word: end_word}
        chains = read_rt(args.rt_file)

        # Make dict mapping the end word of each chain to its start word
        # Due to chain collisions, end_word may map to multiple start_words
        # Has format {end_word: [start_word(s)]}
        chains_rev = {}
        for start_word, end_word in chains.items():
            if chains_rev.get(end_word) is None:
                chains_rev[end_word] = []
            chains_rev[end_word].append(start_word)

        # Iterate over each hash in hashes
        cracked_passwds = []
        for passwd_hash in hashes:

            # Iterate from i = k - 1 downto 0
            possible_start_words = []
            for i in range(args.k-1, -1, -1):
                # Compute hash chain of passwd_hash starting from position i
                # TODO: Implement this!
                m = get_word(wordlist, passwd_hash, i)
                if (m in chains_rev):
                    getstart = chains_rev.get(m)
                    for i in range(len(getstart)):
                        possible_start_words.append(getstart[i])
            # We might have found multiple start words if collisions happened.
            # Compute the entire hash chain for each possible start word and
            # check if passwd_hash is inside of it. If it is, find the plaintext
            # that hashes to passwd_hash and store it in cracked_passwd.
            cracked_passwd = None
            # TODO: Implement this!
            for i in range(len(possible_start_words)):
                m = possible_start_words[i]
                for j in range(args.k-1):
                    h = H(m)
                    m = R(wordlist, h, j)
                    if (h in hashes):
                        cracked_passwd = m
                        cracked_passwds.append(cracked_passwd)  
            # Append cracked password to cracked_passwds
            # (Or append None if we didn't find a password)
        # Print out all of the cracked passwords
        print("\n" + "Cracked passwords:")
        for passwd_hash, cracked_passwd in zip(hashes, cracked_passwds):
            print("{}\t{}".format(passwd_hash, cracked_passwd))
        
        

    else:
        print("Invalid mode. Use python hw2.py -h for help.")