#include "Board.h"
#include "Header3Defs.h"
#include <iostream>
#include <fstream>
#include <string>

//slice character file lines into usable data
string lineSlicing(int character, int data) {
    fstream CharacterFile("Characters.txt");
    if (CharacterFile.fail()) {
        cout << "File failed to open" << endl;
        exit(-1);
    }
    string array[6][6], line;
    int linecount = 0;

    while (getline(CharacterFile, line)) {
        int barCount = 0, length = line.length();
        for (int i = 0; i < length; i++) {
            if (line[i] == '|') {
                barCount++;
            }
            else {
                array[linecount][barCount] = array[linecount][barCount].append(line.substr(i,1));
            }
        }
        linecount++;
    }
    return(array[character][data]);
}

//prompt players to choose characters and display character stats
void Characters::CharacterSelection(Characters p1, Characters p2) {
    
    cout << "Available characters:" << endl;
    string lines;
    int intc1, intc2;
    //display character data here
    cout << "Player 1 character(type 1-5): ";
    cin >> intc1;
    cout << endl << "Character " << intc1 << " was chosen. They are no longer available for selection." << endl;
    cout << "Player 2 character(type 1-5): ";
    cin >> intc2;
    if (intc2 == intc1) {
        cout << "That character has already been chosen. Please choose another character: ";
        cin >> intc2;
    }
    cout << endl << "Character " << intc2 << " was chosen. Both players have chosen characters.";

    p1.name = lineSlicing(intc1, 0);
    p2.name = lineSlicing(intc2, 0);    
}

void CharacterSettings(Characters p1, Characters p2);