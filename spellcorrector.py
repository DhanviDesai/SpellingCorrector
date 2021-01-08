import re
import pandas as pd

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
                                   dp[i-1][j-1])      # Replace
 
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

    if(len(union) == 0):
        return -1
    #Jaccardian co-efficent = |X n Y| / |X u Y|
    else:
        return len(intersection)/len(union)

def get_aff_en(words,aff_rules):
    word_list = []
    for word in words:
        if('/' in word):
            root_word = word.split('/')[0]
            word_list.append(root_word)
            for r in re.split('(?=[A-Z])(?<!^)',word.split('/')[1]):
                pfx_rule = "PFX "+r
                if re.search(pfx_rule,aff_rules):
                    curr_rule = [aff_rules[m.start(0):m.end(0)].split() for m in re.finditer("PFX "+r+" .*",aff_rules)]
                    l_rules = int(curr_rule[0][3])
                    for i in range(1,l_rules+1):
                        if(re.search(curr_rule[i][4]+"$",root_word)):
                            word_list.append(curr_rule[i][3]+root_word)
                else:
                    # print("SFX "+r+" .*")
                    curr_rule = [aff_rules[m.start(0):m.end(0)].split() for m in re.finditer("SFX "+r+" .*",aff_rules)]
                    if(len(curr_rule)==0):
                        continue
                    # print(curr_rule)
                    l_rules = int(curr_rule[0][3])
                    for i in range(1,l_rules+1):
                        if(re.search(curr_rule[i][4]+"$",root_word)):
                            if(curr_rule[i][2] == '0'):
                                word_list.append(root_word+curr_rule[i][3])
                            else:
                                # print('Here',curr_rule[i])
                                word_list.append(re.sub(curr_rule[i][2]+"$",curr_rule[i][3],root_word))         
        else:
            word_list.append(word)
    return word_list

#--------TODO---------
#Handle capitalization
#Handle compund words
#---------------------


def correct_sentences(df):

    return_sent_list = []

    with open("dictionary_files\\en.dic","r") as f:
        txt = f.read()

    with open("dictionary_files\\en.aff","r") as f:
        aff_rules = f.read()

    for sent in df[0]:
        
        corr_sent = ''

        for w in re.split(r'\b',sent):
            w = w.lower()

            if(not w.isalpha() or re.search(r"\b"+w+r"\b",txt)):
                corr_sent += " "+w
                continue
            else:
                # print(w)
                bi = [w[i]+w[i+1] for i in range(len(w) - 2)]
                
                found = False

                consider_index = 0

                while(not found):
                    patt = r".*"+bi[consider_index]+r".*"
                    word_list = re.findall(patt,txt)
                    if(len(word_list) > 100):
                        found = True
                    else:
                        consider_index += 1
                
                final_words = get_aff_en(word_list,aff_rules)

                min_ed = 999
                min_word = None

                total_words = []

                for word in final_words:
                    jc = calculate_jc(w,word)
                    if(jc>=0.4):
                        max_jc = jc
                        max_word = word
                        total_words.append((word,jc))
                
                # print_words = []

                for word,jc in total_words:
                    ed = editDistDP(w,word,len(w),len(word))
                    if(ed<min_ed):
                        min_ed = ed
                        min_word = word
                        # print_words.append(word)
                
                corr_sent += " "+min_word

        return_sent_list.append(corr_sent)
    
    return pd.DataFrame(return_sent_list)

if __name__ == "__main__":
    s = [['nonxadpayment amount is not paid.'],['postxadmortem report is not yet available']]
    df = pd.DataFrame(s)
    corr_df = correct_sentences(df)
    for s in corr_df[0]:
        print(s)

