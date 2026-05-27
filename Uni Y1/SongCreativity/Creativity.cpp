#include <iostream>
#include <fstream>
#include <vector>

using namespace std;
//declaration of independence
int indexOfLargest = 0, totaluniquewords = 0, wordtotal = 0;
string line, tempword;
vector<string> wordvector;
vector<int> wordcounts;

char lowercaseify(char c) {
    if (int(c) > 64 && int(c) < 91) {
        return(char(int(c) + 32));
    }
    else {
        return(c);
    }
}

void putitinthere(string& inputword, vector<string>& wordvec, vector<int>& countvec) {
    wordvec.push_back(inputword);
    countvec.push_back(1);
    totaluniquewords++;
    inputword.clear();
}

int main() {
    ifstream file("song.txt");

    if (file.fail()) {
        return(-1);
    }

    while (getline(file, line)) {
        for (char c : line) {
            if ((c != ' ') && (c != '(') && (c != ')') && (c != ',') && (c != '\r')) {
                tempword += lowercaseify(c);
            }
            else {
                if (wordvector.empty()) {
                    putitinthere(tempword, wordvector, wordcounts);
                }
                
                if (!tempword.empty()) {
                    bool found = false;
                    for (int i = 0; i < totaluniquewords; i++) {
                        if (wordvector[i] == tempword) {
                            wordcounts[i]++;
                            found = true;
                            tempword.clear();
                            break;
                        }
                    }
                    if (!found) {
                        putitinthere(tempword, wordvector, wordcounts);
                    }
                }
            }
        }
        wordtotal++;
        tempword.clear();
    }

    for (int i = 0; i < totaluniquewords; i++) {
        if (wordcounts[i] > wordcounts[indexOfLargest]) {
            indexOfLargest = i;
        }
    }
    float percentage = totaluniquewords/wordtotal;
    cout << "There are " << totaluniquewords << " unique words in the song" << endl;
    cout << "This is " << percentage << " percent unique." << endl;
    cout << "The most common word is \"" << wordvector[indexOfLargest] << "\" at " << wordcounts[indexOfLargest] << " times." << endl << endl;

    for (int i = 0; i < totaluniquewords; i++) {
        cout << i + 1 << ": \"" << wordvector[i] << "\" - " << wordcounts[i] << endl;
    }

    return(0);
}