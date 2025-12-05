#include "Board.h"
#include "Header3Defs.h"
#include <iostream>
#include <fstream>
#include <string>

//slice character file lines into usable data
string lineSlicing(string line, int character, int data) {
    fstream CFile("Characters.txt");
    string array[5][6], line;
    int barCount = 0, linecount = 0;

    while (getline(CFile, line)) {
        for (int i = 0; i <= line.length(); i++) {
            if (line[i] == '|') {
                barCount++;
            }
            else {
                array[linecount][barCount] += line[i];
            }
        }
        linecount++;
    }
    return(array[character][data]);
}

//prompt players to choose characters and display character stats
Characters Characters::CharacterSelection(Characters p1, Characters p2) {
    
    cout << "Available characters:" << endl;
    string lines;
    int counter = 0, intc1, intc2;
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

    //p1.name = 
    
}