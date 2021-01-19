#include <iostream>
#include <string>
#include <chrono>
#include <fstream>
#include <vector>
#include <cmath>

struct Node{
    std::string word;
    Node *next_nodes[25];
    Node(std::string w){
        word = w;
        for(int i=0;i<25;i++){
            next_nodes[i] = 0;
        }
    }
};

struct Linked_Node{
    double jaro_similarity;
    std::string word;
    Linked_Node* next_node;
    Linked_Node(){
        jaro_similarity = -1;
        word = "";
        next_node = NULL;
    }
};

Linked_Node *start;

// Function to calculate the 
// Jaro Similarity of two strings 
double jaro_distance(std::string s1, std::string s2) 
{ 
    // If the strings are equal 
    if (s1 == s2) 
        return 1.0; 
  
    // Length of two strings 
    int len1 = s1.length(), 
        len2 = s2.length(); 
  
    if (len1 == 0 || len2 == 0) 
        return 0.0; 
  
    // Maximum distance upto which matching 
    // is allowed 
    int max_dist = floor(std::max(len1, len2) / 2) - 1; 
  
    // Count of matches 
    int match = 0; 
  
    // Hash for matches 
    int hash_s1[s1.length()] = { 0 }, 
        hash_s2[s2.length()] = { 0 }; 
  
    // Traverse through the first string 
    for (int i = 0; i < len1; i++) { 
  
        // Check if there is any matches 
        for (int j = std::max(0, i - max_dist); 
             j < std::min(len2, i + max_dist + 1); j++) 
            // If there is a match 
            if (s1[i] == s2[j] && hash_s2[j] == 0) { 
                hash_s1[i] = 1; 
                hash_s2[j] = 1; 
                match++; 
                break; 
            } 
    } 
  
    // If there is no match 
    if (match == 0) 
        return 0.0; 
  
    // Number of transpositions 
    double t = 0; 
  
    int point = 0; 
  
    // Count number of occurances 
    // where two characters match but 
    // there is a third matched character 
    // in between the indices 
    for (int i = 0; i < len1; i++) 
        if (hash_s1[i]) { 
  
            // Find the next matched character 
            // in second string 
            while (hash_s2[point] == 0) 
                point++; 
  
            if (s1[i] != s2[point++]) 
                t++; 
        } 
  
    t /= 2; 
  
    // Return the Jaro Similarity 
    return (((double)match) / ((double)len1) 
            + ((double)match) / ((double)len2) 
            + ((double)match - t) / ((double)match)) 
           / 3.0; 
} 
  
// Jaro Winkler Similarity 
double jaro_Winkler(std::string s1, std::string s2) 
{ 
    double jaro_dist = jaro_distance(s1, s2); 
  
    // If the jaro Similarity is above a threshold 
    if (jaro_dist > 0.7) { 
  
        // Find the length of common prefix 
        int prefix = 0; 
  
        for (int i = 0; 
             i < std::min(s1.length(), s2.length()); i++) { 
            // If the characters match 
            if (s1[i] == s2[i]) 
                prefix++; 
  
            // Else break 
            else
                break; 
        } 
  
        // Maximum of 4 characters are allowed in prefix 
        prefix = std::min(4, prefix); 
  
        // Calculate jaro winkler Similarity 
        jaro_dist += 0.1 * prefix * (1 - jaro_dist); 
    } 
  
    return jaro_dist; 
} 

int editDistance(std::string& a,std::string& b) 
{ 
    int m = a.length();
    int n = b.length(); 
    int dp[m+1][n+1]; 
  
    // filling base cases 
    for (int i=0; i<=m; i++) 
        dp[i][0] = i; 
    for (int j=0; j<=n; j++) 
        dp[0][j] = j; 
  
    // populating matrix using dp-approach 
    for (int i=1; i<=m; i++) 
    { 
        for (int j=1; j<=n; j++) 
        { 
            if (a[i-1] != b[j-1]) 
            { 
                dp[i][j] = std::min(std::min(1 + dp[i-1][j],  // deletion 
                                1 + dp[i][j-1]),  // insertion 
                                1 + dp[i-1][j-1] // replacement 
                ); 
            } 
            else
                dp[i][j] = dp[i-1][j-1]; 
        } 
    } 
    return dp[m][n]; 
} 

//To add words in bk tree
void add_word(Node *root,std::string word){
    if(root->word == ""){
        root->word = word;
    }
    else{
        int ed = editDistance(root->word,word);
        if(root->next_nodes[ed] == 0){
            Node *temp = new Node(word);
            root->next_nodes[ed] = temp;
        }else{
            add_word(root->next_nodes[ed],word);
        }
    }
}

std::vector<std::string> traverse_bkt(Node *root,std::string word,int tol){
    std::vector<std::string> word_list;
    if(root->word == ""){
        return word_list;
    }
    int ed = editDistance(root->word,word);
    if(ed<=tol){
        word_list.push_back(root->word);
    }
    int start = ed-tol;
    if(start <= 0){
        start = 1;
    }
    while(start <= ed+tol){
        if(root->next_nodes[start] != 0){
        std::vector<std::string> tmp = traverse_bkt(root->next_nodes[start],word,tol);
        for(std::string t : tmp)
            word_list.push_back(t);
        }
        
        start++;
    }
    return word_list;
}

void print_nodes(std::string parent,Node *root,int index){
    std::cout<<"Parent :"<<parent<<" "<<root->word<<" "<<index<<std::endl;
    for(int i=0;i<25;i++){
        if(root->next_nodes[i] != 0){
            print_nodes(root->word,root->next_nodes[i],i);
        }
    }
}

void initialize_list(){
    start = new Linked_Node();
}

void add_node_sort(double sim,std::string word){
    if(start->word == ""){
        start->word = word;
        start->jaro_similarity = sim;
    }else{
        Linked_Node *temp = start;
        Linked_Node *prev = start;
        Linked_Node *new_node = new Linked_Node();
        new_node->word = word;
        new_node->jaro_similarity = sim;
        while(temp != NULL && temp->jaro_similarity >= sim){
            prev = temp;
            temp = temp->next_node;
        }
        //Insert at the start of the list
        if(temp == start){
            new_node->next_node = temp;
            start = new_node;
        }
        //Insert at the end of the list
        else if(temp == NULL){
            prev->next_node = new_node;
        }
        //Insert in between the list
        else{
            new_node->next_node = temp;
            prev->next_node = new_node;
        }
    }
}

void traverse_list(){
    Linked_Node *temp = start;
    while(temp != NULL){
        std::cout<<temp->word<<" ";
        temp = temp->next_node;
    }
    std::cout<<std::endl;
}

void delete_list(){
    free(start);
}

/*

TODO:
---Separate code into different segments:
---Create a method to initialize dictionary
---Method to free memory

*/


int main(int argv, char** argc){
    Node root = Node("");
    std::fstream newfile;
    newfile.open("txt_files\\all_words_every.txt",std::ios::in);
   if (newfile.is_open()){
      std::string tp;
      while(getline(newfile, tp)){
         add_word(&root,tp);
      }
      newfile.close();
   }    
    std::cout<<"Shabda 0.0.0"<<std::endl;

    while(1){
        initialize_list();
        std::string w;
        std::cin>>w;
        std::vector<std::string> l = traverse_bkt(&root,w,ceil(w.length()/3));
        for(std::string a:l){
            double temp = jaro_distance(a,w);
            add_node_sort(temp,a);
        }
        traverse_list();
        // std::cout<<std::endl;
        delete_list();
    }
    
    return 0;

}


