#include <iostream>
#include <fstream>
#include <vector>

using namespace std;

int main() {
    string line, word;
    bool existsAlready = false;
    vector<string> words;
    vector<int> wordcounts;
    int indexOfLargest = 0;

    ifstream file("song.txt");

    if (file.fail()) {
        return(-1);
    }

    while (getline(file, line)) {
        for (int i = 0; i < line.length(); i++) {
            if (line[i] != ' ') {
                word += line[i];
            }
            else {
                for (int i = 0; i < words.size(); i++) {
                    if (words[i] == word) {
                        existsAlready = true;
                        wordcounts[i]++;
                    }
                }
                if (!existsAlready) {
                    words.push_back(word);
                    wordcounts.push_back(1);
                    word = "";
                    existsAlready = false;
                }
            }
        }
    }
    for (int i : wordcounts) {
        if (wordcounts[i] > wordcounts[indexOfLargest]) {
            indexOfLargest = i;
        }
    }
    cout << "The most common word is " << words[indexOfLargest] << " at " << wordcounts[indexOfLargest] << " times." << endl;

    return(0);
}