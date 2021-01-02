import json
import os

#Calculate the edit distance to convert str1 to str2
def editDistDP(str1, str2, m, n):
    # Create a table to store results of subproblems
    dp = [[0 for x in range(n + 1)] for x in range(m + 1)]
 
    # Fill d[][] in bottom up manner
    for i in range(m + 1):
        for j in range(n + 1):
 
            # If first string is empty, only option is to
            # insert all characters of second string
            if i == 0:
                dp[i][j] = j    # Min. operations = j
 
            # If second string is empty, only option is to
            # remove all characters of second string
            elif j == 0:
                dp[i][j] = i    # Min. operations = i
 
            # If last characters are same, ignore last char
            # and recur for remaining string
            elif str1[i-1] == str2[j-1]:
                dp[i][j] = dp[i-1][j-1]
 
            # If last character are different, consider all
            # possibilities and find minimum
            else:
                dp[i][j] = 1 + min(dp[i][j-1],        # Insert
                                   dp[i-1][j],        # Remove
                                   dp[i-1][j-1])    # Replace
 
    return dp[m][n]
    
#Calculate the Jaccardian co-efficient between the two bigrams
def calculate_jc(bigram1,bigram2):

    #Create a set from the two bigram lists
    set_a = set(bigram1)
    set_b = set(bigram2)
    
    #Find the intersection between the two sets
    intersection = set_a.intersection(set_b)

    #Find the union between the two sets
    union = set_a.union(set_b)

    #Jaccardian co-efficent = |X n Y| / |X u Y|
    return len(intersection)/len(union)

#Query word
w = "freadom"

#Create bigram of the query word
bi = [""+w[i]+w[i+1] for i in range(len(w)-1)]

#Dictionaries to keep track of the essentials
    #Keeps track of the list of words with each bigram
bi_words_dict = {}
    #Keeps track of the pointer to each list. Each bigram is stored as the key and it contains a list with 2 items: the current word that it points to and the current index
bi_words_pointer = {}

#Initialize the above dictionaries
for gram in bi:
    bi_words_dict[gram] = []
    bi_words_pointer[gram] = 0

#Keeps track of worthy candidates to calculate edit distance
answer_list = []

#Keeps track of all the words in dictionary
real_words_dict = {}

#Read the dictionary and save the words
with open(os.path.join(os.getcwd,"json_files","dictionary-json.json"),"r") as openfile:
    real_words_dict = json.load(openfile)

#Create the list of words with atleast one bigram
for word_key in real_words_dict.keys():
    for gram in bi:
        if gram in real_words_dict[word_key]:
            bi_words_dict[gram].append(word_key)

#List to keep track of pointers at the end of the list
pointersAtEndList = []

#Run until all the pointers (bi-gram keys) have reached the end of the list
while(len(pointersAtEndList) < len(bi_words_pointer.keys())):

    #Senteinel variables to find the lexicographically small word out of all the words that are being pointed
    small_word = None
    small_key = None

    #Traverse all the bi-gram lists to add worthy candidates
    for key in bi_words_dict.keys():

        #When pointer reaches the end of the list, add it to the list
        if( bi_words_pointer[key] == len(bi_words_dict[key]) - 1):
            pointersAtEndList.append(key)

        #Initialize the sentinel variables to current word
        elif(small_word is None or small_key is None):
            small_word = bi_words_dict[key][bi_words_pointer[key]]
            small_key = key

        #If the current word is smaller than the small word, update the sentinel variables
        elif(bi_words_dict[key][bi_words_pointer[key]] < small_word):
            small_word = bi_words_dict[key][bi_words_pointer[key]]
            small_key = key
        
        #If current word is equal to small word ( tie situation ) then update both the pointers
        elif(bi_words_dict[key][bi_words_pointer[key]] == small_word):
            if(bi_words_pointer[key] < len(bi_words_dict[key]) - 1): 
                bi_words_pointer[key] += 1
            if(bi_words_pointer[small_key] < len(bi_words_dict[small_key]) - 1):
                bi_words_pointer[small_key] += 1
            jc = calculate_jc(bi,real_words_dict[small_word])
            if((small_word,jc) not in answer_list):
                answer_list.append((small_word,jc))
    
    #After traversal of bi-gram list increment the pointer
    if(bi_words_pointer[small_key] < len(bi_words_dict[small_key]) - 1):
        bi_words_pointer[small_key] += 1

#Sentinel variables to find the word with minimum edit distance
min_dist = 999
min_word = None

#Traverse all the words short-listed from n-gram similarity to find the word with minimum edit distance
for wt in answer_list:
    #If Jaccardian co-efficent of the word is greater than 0.45 consider it for edit distance calculation
    if(wt[1]>0.45):
        min_val = editDistDP(w,wt[0],len(w),len(wt[0]))
        if(min_val < min_dist):
            min_dist = min_val
            min_word = wt[0]

print(min_word)

