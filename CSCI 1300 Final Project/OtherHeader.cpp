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
            if (line[i] == '\r') continue;
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
void CharacterSelection() {
    
    cout << "Available characters:" << endl;
    for (int i = 1; i < 6; i++) {
        cout << lineSlicing(i, 0) << endl;
    }
    cout << "Player 1 character(type 1-5): ";
    cin >> Character1;
    cout << "Player 1 chose " << lineSlicing(Character1, 0) << ". They are no longer available for selection." << endl;
    cout << "Player 2 character(type 1-5): ";
    cin >> Character2;
    //input validation may require more work
    if (Character2 == Character1) {
        cout << "That character has already been chosen. Please choose another character: ";
        cin >> Character2;
    }
    cout << "Player 2 chose " << lineSlicing(Character2, 0) << ". Both players have chosen characters." << endl;
}

//constructor to initialize variables based on character choice
Characters::Characters(int c) {
    name = lineSlicing(c, 0);
    Exp = stoi(lineSlicing(c, 1));
    Acc = stoi(lineSlicing(c, 2));
    Eff = stoi(lineSlicing(c, 3));
    Ins = stoi(lineSlicing(c, 4));
    Dsp = 20000;
}

void Characters::PrintStats(int player) {
    cout << "Player " << player << " stats: " << endl;
    cout << "Name:" << name << endl;
    cout << "Experience: " << Exp << endl;
    cout << "Accuracy: " << Acc << endl;
    cout << "Efficiency: " << Eff << endl;
    cout << "Insight: " << Ins << endl;
    cout << "Discovery Points: " << Dsp << endl;
}

void Characters::PathSelection() {
    int pathChoice;
    cout << "Both players must now choose a path. This will determine the course of the game." << endl;
    cout << "Players can either choose the Training Fellowship path, offering high stat boosts" << endl;
    cout << "and an advisor but a significant discovery point cost, or the Direct Lab Assistant" << endl;
    cout << "path, coming with a significant boost in discovery points, a smaller stat boost," << endl;
    cout << "but no advisor. Please choose wisely!" << endl;

    cout << "Player 1 - select 1 for Training Fellowship or 2 for Direct Lab Assistant: ";
    cin >> pathChoice;
    if (pathChoice == 1) {
        path = 1;
    }
    else if (pathChoice == 2) {
        path = 0;
    }
    else {
        //add more to this later?
        cout << "Invalid choice";
    }
}
