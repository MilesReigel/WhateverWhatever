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
    string array[7][6], line;
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
    for (int i = 1; i < 7; i++) {
        cout << lineSlicing(i, 0) << endl;
    }
    cout << "Player 1 character(type 1-6): ";
    cin >> Character1;
    cout << "Player 1 chose " << lineSlicing(Character1, 0) << ". They are no longer available for selection." << endl;
    cout << "Player 2 character(type 1-6): ";
    cin >> Character2;
    //input validation may require more work
    if (Character2 == Character1) {
        cout << "That character has already been chosen. Please choose another character: ";
        cin >> Character2;
    }
    cout << "Player 2 chose " << lineSlicing(Character2, 0) << ". Both players have chosen characters." << endl << endl;
}

//constructor to initialize variables based on character choice
Characters::Characters(int p, int c) {
    name = lineSlicing(c, 0);
    number = p;
    Exp = stoi(lineSlicing(c, 1));
    Acc = stoi(lineSlicing(c, 2));
    Eff = stoi(lineSlicing(c, 3));
    Ins = stoi(lineSlicing(c, 4));
    Dsp = 20000;
    advisor = 0;
    path = false;
}

//function to print character stats
void Characters::PrintStats(int player, int typeOfCall) {
    cout << endl << "Player " << player << " stats: " << endl;
    cout << "Name: " << name << endl;
    switch (typeOfCall) {
        case 1:
            cout << "Experience: " << Exp << endl;
            cout << "Advisor: " << AdvisorPrinting(advisor) << endl;
        case 2:
            cout << "Accuracy: " << Acc << endl;
            cout << "Efficiency: " << Eff << endl;
            cout << "Insight: " << Ins << endl;
            cout << "Discovery Points: " << Dsp << endl << endl;
            break;
        default:
            cout << "Experience: " << Exp << endl;
            cout << "Advisor: " << AdvisorPrinting(advisor) << endl;
            cout << "Accuracy: " << Acc << endl;
            cout << "Efficiency: " << Eff << endl;
            cout << "Insight: " << Ins << endl;
            cout << "Discovery Points: " << Dsp << endl << endl;
    }
    
    
}

//player path selection function
void Characters::PathSelection(int player) {
    int pathChoice;
    cout << "Both players must now choose a path. This will determine the course of the game." << endl;
    cout << "Players can either choose the Training Fellowship path, offering high stat boosts" << endl;
    cout << "and an advisor but a significant discovery point cost, or the Direct Lab Assistant" << endl;
    cout << "path, coming with a significant boost in discovery points, a smaller stat boost," << endl;
    cout << "but no advisor. Please choose wisely!" << endl << endl;

    cout << "Player " << player << " - select 1 for Training Fellowship or 2 for Direct Lab Assistant: ";
    cin >> pathChoice;
    if ((pathChoice != 1) && (pathChoice != 2)) {
        //add more input validation if time permits
        cout << "Invalid choice, please try again (type 1 or 2): ";
        cin >> pathChoice;
    }
    //change path variables
    if (pathChoice == 1) {
        path = true;
        Acc += 500;
        Eff += 500;
        Ins += 1000;
        Dsp -= 5000;
        cout << "Your new stats are: " << endl;
        PrintStats(player, 3);

    }
    else {
        path = false;
        Acc += 200;
        Eff += 200;
        Ins += 200;
        Dsp += 5000;
        cout << "Your new stats are: " << endl;
        PrintStats(player, 3);
    }
}

//advisor selection
void Characters::AdvisorSelection(int player) {
    cout << "Player " << player << " has chosen the Training Fellowship Path. This player must" << endl;
    cout << "now choose an advisor to guide them on their journey. The advisor options are as" << endl;
    cout << "follows: " << endl;
    cout << "1. Dr. Aliquot - A master of the \"wet lab\", assisting in avoiding contamination." << endl;
    cout << "2. Dr. Assembler - An expert who helps improve efficiency and streamlines pipelines" << endl;
    cout << "3. Dr. Pop-Gen - A genetics specialist with insight for identifying rare genetic variants." << endl;
    cout << "4. Dr. Bio-Script - The genius behind the data analysis, helps debug code." << endl;
    cout << "5. Dr. Loci - Your biggest supporter assisting you in learning the equipment" << endl;
    cout << "Please type (1-5) your choice: ";
    cin >> advisor;

    if ((advisor < 0) || (advisor > 5)) {
        cout << "Invalid choice - please choose again: ";
        cin >> advisor;
    }

    cout << endl << "You have chosen Dr. ";
    switch (advisor) {
        case 1:
            cout << "Aliquot";
            break;
        case 2:
            cout << "Assembler";
            break;
        case 3:
            cout << "Pop-Gen";
            break;
        case 4:
            cout << "Bio-Script";
            break;
        case 5:
            cout << "Loci";
            break;
    }
    cout << ". They will aid you on your journey to become the best genomist!" << endl << endl;
}

string Characters::AdvisorPrinting(int advisor) {
    switch (advisor) {
        case 1:
            return("Aliquot, master of the \" wet lab\"");
            break;
        case 2:
            return("Assembler, optimizer of pipelines");
            break;
        case 3:
            return("Pop-Gen, a genetic-variant-identifying specialist");
            break;
        case 4:
            return("Bio-Script, genius data analyst");
            break;
        case 5:
            return("Loci, your friendly neighborhood equipment specialist");
            break;
        default:
            return("N/A");
    }
}


//riddle calling function
string riddles(int riddlenum, bool riddleorans) {
    fstream RiddleFile("riddles.txt");
    if (RiddleFile.fail()) {
        cout << "File failed to open" << endl;
        exit(-1);
    }
    string riddle[2], line;
    int linecounter = 0;
    bool passed = false;

    while (getline(RiddleFile, line)) {
        int length = line.length();
        if (linecounter == riddlenum) {
            for (int i = 0; i < length; i++) {
                if (line[i] == '\r') continue;
                if (line[i] == '|') {
                    passed = true;
                }
                else if (!passed){
                    riddle[0] = riddle[0].append(line.substr(i, 1));
                }
                else {
                    riddle[1] = riddle[1].append(line.substr(i, 1));
                }
            }
        }
        linecounter++;
    }
    if (riddleorans) {
        return(riddle[0]);
    }
    else {
        return(riddle[1]);
    }
}

void Characters::events() {
    int eventnum = rand() % 48;
    fstream EventsFile("events.txt");
    if (EventsFile.fail()) {
        cout << "File failed to open" << endl;
        exit(-1);
    }
    string event[4], line;
    int linecounter = 0;

    while (getline(EventsFile, line)) {
        int length = line.length(), barcounter = 0;
        if (linecounter == eventnum) {
            for (int i = 0; i < length; i++) {
                if (line[i] == '\r') continue;

                if (line[i] == '|') {
                    barcounter++;
                }
                else {
                    event[barcounter] = event[barcounter].append(line.substr(i, 1));
                }
            }
        }
        linecounter++;
    }

    cout << event[0] << "." << endl;
    if ((event[1] == "0") && (event[2] != "0") && (advisor == stoi(event[2]))) {
        cout << "Your advisor has saved you from misfortune! Your Discovery Points live to see" << endl;
        cout << "another day." << endl;
    }
    else {
        if (stoi(event[3]) > 0) {
            cout << "This is fortunate. + " << event[3] << " Discovery Points" << endl;
            Dsp += stoi(event[3]);
        }
        else {
            cout << "This is unfortunate. Better luck next time! " << endl;
            cout << event[3] << " Discovery Points" << endl;
            Dsp += stoi(event[3]);
        }
    }
    
}

void Characters::misfortune(int player) {
    cout << "A surprise event has struck player " << player << "!" << endl;
    //riddle
    if ((rand() % 2) == 1) {
        string answer;
        cout << "player " << player << "must solve a riddle: " << endl << endl;
        int lineSelection = rand() % 25;
        cout << riddles(lineSelection, true) << endl;
        cin >> answer;
        if (riddles(lineSelection, false) == answer) {
            cout << "Wowie, you got it! That question was pretty easy though." << endl << "+500 Discovery Points" << endl;
            Dsp += 500;
        }
        else {
            cout << "Haha I bet you wish that were the answer! It's actually " << riddles(lineSelection, false) << endl;
            cout << "You failed so badly that you get a penalty!" << endl;
            cout << "-500 Discovery Points for not paying more attention in class" << endl;
            Dsp -= 500;
        }
    }
    //event
    else {
        events();
    }
}

void turn(int player, Board BigB, Characters character) {
    int choice;
    cout << endl << "It is player " << player << "'s turn! choose one of the options below: " << endl;
    cout << "1: Roll your dice to move forward" << endl;
    cout << "2: Check your character stats" << endl;
    cout << "3: Check board position" << endl;
    cout << "4: Attempt to sabotage the other player" << endl;
    cout << "5: Gamble?" << endl << endl;
    cout << "Enter your choice: ";
    cin >> choice;
    switch (choice) {
        case 1:
            //ideally this can still modify class objeect variables like player position for bigb, we will see
            BigB.movePlayer(BigB.RollDice(player));
            break;
        case 2:
            cout << "Would you like to see Experience and Advisor(1) or Discovery Points and other stats(2)? " << endl;
            cin >> choice;
            if (choice == 1) {
                character.PrintStats(player, 1);
            }
            else if (choice == 2) {
                character.PrintStats(player, 2);
            }
            else {
                cout << "That wasn't an option you goof" << endl;
            }
            turn(player, BigB, character);
            break;
        case 3:
            BigB.displayBoard();
            turn(player, BigB, character);
            break;
        case 4:

            break;
        case 5:

            break;
        default:
            cout << "Invalid input, try that sh*t again chief" << endl;
            turn(player, BigB, character);


    }
}